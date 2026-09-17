from dotenv import load_dotenv #type: ignore
import os
import subprocess
import sys
import re
import shutil
import glob
import tempfile
import uuid
import time
import queue
import threading
import asyncio
import json
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends # type: ignore
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from google import genai  # type: ignore
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel, Field, validator

from router.user import userRouter
from libs.cloudinary import upload_video
from middleware import get_current_user_id
from configurations import user_collection

manim_path = shutil.which("manim")

# --- Security: Code Validation ---

# Imports that could allow arbitrary system access
FORBIDDEN_IMPORTS = [
    'os', 'sys', 'subprocess', 'shutil', 'socket', 'requests',
    'http', 'urllib', 'pathlib', 'io', 'ctypes', 'signal',
    'multiprocessing', 'threading', 'asyncio', 'ftplib',
    'smtplib', 'pickle', 'shelve', 'importlib', 'code',
    'codeop', 'compile', 'compileall', 'webbrowser',
]

# Dangerous function calls / builtins
FORBIDDEN_PATTERNS = [
    'exec(', 'eval(', 'compile(', '__import__(',
    'open(', 'globals(', 'locals(', 'getattr(',
    'setattr(', 'delattr(', 'breakpoint(',
    'os.system', 'os.popen', 'subprocess.',
    'input(',
]


def validate_generated_code(code: str) -> tuple[bool, str]:
    """
    Check LLM-generated code for dangerous patterns before execution.
    Returns (is_safe, reason).
    """
    for line in code.splitlines():
        stripped = line.strip()

        # Skip comments
        if stripped.startswith('#'):
            continue

        # Check forbidden imports
        for mod in FORBIDDEN_IMPORTS:
            if re.search(rf'\bimport\s+{re.escape(mod)}\b', stripped):
                return False, f"Forbidden import detected: '{mod}'"
            if re.search(rf'\bfrom\s+{re.escape(mod)}\b', stripped):
                return False, f"Forbidden import detected: 'from {mod}'"

        # Check forbidden function calls / patterns
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in stripped:
                return False, f"Forbidden pattern detected: '{pattern}'"

    return True, "Code passed validation"


# --- Configuration ---

MAX_PROMPT_LENGTH = 2000  # characters

class PromptRequest(BaseModel):
    prompt: str
    conversationId: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @validator('prompt')
    def validate_prompt(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Prompt cannot be empty')
        if len(v) > MAX_PROMPT_LENGTH:
            raise ValueError(f'Prompt too long (max {MAX_PROMPT_LENGTH} characters)')
        return v

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()
origins = [
     "https://cursor-for-2-danimation.vercel.app",
     "https://cursor-for-2d-anim-vid.vercel.app"
     "http://localhost:5173"
]
app.include_router(userRouter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            
    allow_credentials=True,
    allow_methods=["*"],              
    allow_headers=["*"],              
)

# --- System prompt hardened to discourage dangerous code ---

SYSTEM_PROMPT = (
    "You are a Manim expert. Return only valid Manim Community Edition Python code. "
    "Do not include any explanations or comments. Return just the code block, nothing else. "
    "CRITICAL RULES: "
    "1. ONLY import from 'manim'. Do NOT import os, sys, subprocess, shutil, socket, requests, "
    "   pathlib, io, or any other standard library or third-party module. "
    "2. Do NOT use open(), exec(), eval(), __import__(), input(), or any file/system operations. "
    "3. Do NOT use scipy, numpy, or networkx. Use only core Manim features. "
    "4. Keep the code minimal, with exactly one class that extends Scene. "
    "5. Add the import statement for manim at the top."
)

# --- Gemini free-tier models to try, in order of preference ---
GEMINI_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-2.5-flash",
]

MAX_RETRIES_PER_MODEL = 3
INITIAL_RETRY_DELAY = 3  # seconds, doubles each retry (exponential backoff)


def _is_retryable_error(error_str: str) -> bool:
    """Check if an error is a rate-limit or transient error worth retrying."""
    retryable_keywords = [
        "429", "rate", "quota", "resource_exhausted", "resourceexhausted",
        "503", "overloaded", "unavailable", "connection", "timeout",
        "too many requests", "retry",
    ]
    error_lower = error_str.lower()
    return any(keyword in error_lower for keyword in retryable_keywords)


def call_llm_with_fallback(client, user_prompt, status_callback=None):
    """
    Try each Gemini model in order. Retry each model up to MAX_RETRIES_PER_MODEL
    times with exponential backoff on rate-limit/transient errors before
    falling through to the next model.
    """
    last_error = None
    for model_idx, model_id in enumerate(GEMINI_MODELS):
        for attempt in range(1, MAX_RETRIES_PER_MODEL + 1):
            try:
                msg = f"Generating code with {model_id} (attempt {attempt}/{MAX_RETRIES_PER_MODEL})..."
                print(f"  {msg}", flush=True)
                if status_callback:
                    status_callback(msg)

                chat = client.chats.create(
                    model=model_id,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                    ),
                )
                response = chat.send_message(user_prompt)
                print(f"  ✅ Success with {model_id}", flush=True)
                return response
            except Exception as e:
                last_error = e
                error_str = str(e)

                if _is_retryable_error(error_str):
                    # Exponential backoff with jitter: 3s, 6s, 12s...
                    import random
                    delay = INITIAL_RETRY_DELAY * (2 ** (attempt - 1)) + random.uniform(0, 1)
                    print(f"  ⚠️ {model_id} attempt {attempt} rate-limited: {error_str[:120]}", flush=True)

                    if attempt < MAX_RETRIES_PER_MODEL:
                        retry_msg = f"Model {model_id} rate-limited. Retrying in {delay:.1f}s..."
                        print(f"  ⏳ {retry_msg}", flush=True)
                        if status_callback:
                            status_callback(retry_msg)
                        time.sleep(delay)
                        continue
                    else:
                        # Exhausted retries for this model — cooldown before next model
                        if model_idx < len(GEMINI_MODELS) - 1:
                            next_model = GEMINI_MODELS[model_idx + 1]
                            fallback_msg = f"Model {model_id} rate limit reached. Trying fallback model {next_model}..."
                            print(f"  ⏳ {fallback_msg}", flush=True)
                            if status_callback:
                                status_callback(fallback_msg)
                            time.sleep(3)
                        break
                else:
                    # Non-retryable error — skip to next model immediately
                    print(f"  ❌ {model_id} non-retryable error: {error_str[:120]}", flush=True)
                    break

    raise Exception(f"All AI models are temporarily rate-limited. Please try again in a minute. Last error: {last_error}")


MAX_RENDER_RETRIES = 3  # How many times to re-generate code if Manim rendering fails


@app.post("/generate_video")
async def generate_video(promptRequest: PromptRequest, user_id: str = Depends(get_current_user_id)):
    event_queue = queue.Queue()

    def send_status(msg: str):
        event_queue.put({"type": "status", "message": msg})

    def log(msg: str):
        print(msg, flush=True)

    def worker():
        request_id = str(uuid.uuid4())[:8]
        work_dir = os.path.join(os.getcwd(), "tmp_renders", request_id)
        os.makedirs(work_dir, exist_ok=True)

        try:
            send_status("Initializing video generation...")

            last_render_error = None

            for render_attempt in range(1, MAX_RENDER_RETRIES + 1):
                log(f"[{request_id}] === Render attempt {render_attempt}/{MAX_RENDER_RETRIES} ===")

                if render_attempt > 1:
                    send_status(f"Render attempt {render_attempt}/{MAX_RENDER_RETRIES} — Regenerating code...")

                # --- Step 1: Generate code from LLM ---
                user_prompt = f"Create a Manim animation to explain: {promptRequest.prompt}"
                if render_attempt > 1 and last_render_error:
                    user_prompt += f"\n\nIMPORTANT: The previous attempt failed to render with the following error:\n{last_render_error}\nPlease fix any syntax or rendering errors in the Python Manim code."

                try:
                    response = call_llm_with_fallback(
                        client,
                        user_prompt=user_prompt,
                        status_callback=send_status
                    )
                except Exception as llm_err:
                    # LLM completely failed (all models exhausted) — no point retrying render
                    raise llm_err

                if response is None:
                    event_queue.put({"type": "error", "message": "No response from LLM"})
                    return

                code = response.text
                cleaned_code = code.replace("```python", "").replace("```", "").strip()

                # --- Step 2: Validate code safety ---
                is_safe, reason = validate_generated_code(cleaned_code)
                if not is_safe:
                    log(f"[{request_id}] ⚠️ Code validation failed: {reason}")
                    last_render_error = f"Generated code failed safety check: {reason}"
                    if render_attempt < MAX_RENDER_RETRIES:
                        send_status(f"Generated code had safety issues. Retrying ({render_attempt}/{MAX_RENDER_RETRIES})...")
                        continue
                    else:
                        event_queue.put({
                            "type": "error",
                            "message": "Generated code had syntax/validation errors after 3 attempts. Please try again after some time."
                        })
                        return

                # --- Step 3: Write code & render with Manim ---
                send_status("Code generated! Rendering animation...")

                # Clean up previous render artifacts
                scene_file = os.path.join(work_dir, "scene.py")
                media_dir = os.path.join(work_dir, "media")
                if os.path.exists(media_dir):
                    shutil.rmtree(media_dir, ignore_errors=True)

                with open(scene_file, "w", encoding="utf-8") as f:
                    f.write(cleaned_code)

                match = re.search(r"class\s+(\w+)\s*\(\s*Scene\s*\):", cleaned_code)
                class_name = match.group(1) if match else "GeneratedScene"
                log(f"[{request_id}] Rendering class: {class_name}")

                env = os.environ.copy()
                log_file = os.path.join(work_dir, "render.log")

                render_success = False
                with open(log_file, "w") as f:
                    try:
                        result = subprocess.run(
                            [
                                "manim",
                                scene_file,
                                class_name,
                                "-ql",
                                "--output_file", f"{class_name}.mp4",
                                "--media_dir", media_dir,
                            ],
                            cwd=work_dir,
                            env=env,
                            stdout=f,
                            stderr=subprocess.STDOUT,
                            check=True,
                            start_new_session=True,
                            timeout=500
                        )
                        render_success = True
                    except subprocess.CalledProcessError as e:
                        log(f"[{request_id}] Render failed (attempt {render_attempt}). Return code: {e.returncode}")
                        render_log_snippet = ""
                        try:
                            with open(log_file, "r") as lf:
                                render_log = lf.read()
                            render_log_snippet = render_log[-500:]
                            log(f"[{request_id}] Render log:\n{render_log_snippet}")
                        except Exception:
                            pass
                        last_render_error = render_log_snippet if render_log_snippet else "Manim rendering failed due to code syntax error."

                if render_success:
                    log(f"[{request_id}] ✅ Render succeeded on attempt {render_attempt}")
                    break
                else:
                    if render_attempt < MAX_RENDER_RETRIES:
                        send_status(f"Manim code had syntax/render errors. Regenerating code (attempt {render_attempt + 1}/{MAX_RENDER_RETRIES})...")
                        continue
                    else:
                        send_status("All 3 render attempts failed.")
                        event_queue.put({
                            "type": "error",
                            "message": "Generated code had syntax errors after 3 attempts. Please try again after some time."
                        })
                        return

            # --- Step 4: Find & upload video ---
            send_status("Rendering completed! Uploading video...")
            output_dir = os.path.join(work_dir, "media", "videos", "scene", "480p15")
            filename = f"{class_name}.mp4"
            video_path = os.path.join(output_dir, filename)

            if not os.path.exists(video_path):
                for root, dirs, files in os.walk(os.path.join(work_dir, "media")):
                    for file in files:
                        if file.endswith(".mp4"):
                            video_path = os.path.join(root, file)
                            break

                if not os.path.exists(video_path):
                    event_queue.put({"type": "error", "message": "Video file not found after rendering"})
                    return

            log(f"[{request_id}] Uploading video: {video_path}")
            url = upload_video(video_path)
            log(f"[{request_id}] Upload done: {url}")

            video_data = {
                "prompt": promptRequest.prompt,
                "url": url,
                "conversationId": promptRequest.conversationId,
                "timestamp": promptRequest.timestamp,
            }
            update_result = user_collection.update_one(
                {"auth0_id": user_id},
                {"$push": {"videos": video_data}}
            )

            if update_result.modified_count != 1:
                event_queue.put({"type": "error", "message": "Video saved to DB failed."})
                return

            event_queue.put({"type": "success", "message": "✅ Video generated successfully!", "data": {"url": url}})

        except subprocess.TimeoutExpired:
            log(f"[{request_id}] Rendering timed out")
            event_queue.put({"type": "error", "message": "Rendering timed out."})
        except Exception as e:
            error_msg = str(e)
            log(f"[{request_id}] Worker exception: {error_msg[:300]}")
            if "rate-limited" in error_msg.lower() or "models exhausted" in error_msg.lower():
                event_queue.put({"type": "error", "message": "All AI models are temporarily rate-limited. Please try again in a minute."})
            else:
                event_queue.put({"type": "error", "message": f"Unexpected error: {error_msg[:200]}"})
        finally:
            try:
                shutil.rmtree(work_dir, ignore_errors=True)
            except Exception:
                pass
            event_queue.put(None)  # Sentinel to end stream

    threading.Thread(target=worker, daemon=True).start()

    async def event_generator():
        while True:
            try:
                item = event_queue.get_nowait()
            except queue.Empty:
                await asyncio.sleep(0.1)
                continue

            if item is None:
                break
            yield f"data: {json.dumps(item)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_excludes=["tmp_renders/*", "media/*", "*.log"],
    )
