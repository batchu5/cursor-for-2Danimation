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
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends # type: ignore
from fastapi.middleware.cors import CORSMiddleware
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


def call_llm_with_fallback(client, user_prompt):
    """
    Try each Gemini model in order. Retry each model up to MAX_RETRIES_PER_MODEL
    times with exponential backoff on rate-limit/transient errors before
    falling through to the next model.
    """
    last_error = None
    for model_idx, model_id in enumerate(GEMINI_MODELS):
        for attempt in range(1, MAX_RETRIES_PER_MODEL + 1):
            try:
                print(f"  Trying {model_id} (attempt {attempt}/{MAX_RETRIES_PER_MODEL})...")
                chat = client.chats.create(
                    model=model_id,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                    ),
                )
                response = chat.send_message(user_prompt)
                print(f"  ✅ Success with {model_id}")
                return response
            except Exception as e:
                last_error = e
                error_str = str(e)

                if _is_retryable_error(error_str):
                    # Exponential backoff with jitter: 3s, 6s, 12s...
                    import random
                    delay = INITIAL_RETRY_DELAY * (2 ** (attempt - 1)) + random.uniform(0, 1)
                    print(f"  ⚠️ {model_id} attempt {attempt} rate-limited: {error_str[:120]}")

                    if attempt < MAX_RETRIES_PER_MODEL:
                        print(f"  ⏳ Waiting {delay:.1f}s before retry...")
                        time.sleep(delay)
                        continue
                    else:
                        # Exhausted retries for this model — cooldown before next model
                        if model_idx < len(GEMINI_MODELS) - 1:
                            cooldown = 5
                            print(f"  ⏳ Model {model_id} exhausted. Cooling down {cooldown}s before next model...")
                            time.sleep(cooldown)
                        break
                else:
                    # Non-retryable error — skip to next model immediately
                    print(f"  ❌ {model_id} non-retryable error: {error_str[:120]}")
                    break

    raise Exception(f"All Gemini models exhausted. Last error: {last_error}")

   
@app.post("/generate_video")
async def generate_video(promptRequest: PromptRequest, user_id: str = Depends(get_current_user_id)):
    # Create a unique temp directory for this request to prevent race conditions
    request_id = str(uuid.uuid4())[:8]
    work_dir = os.path.join(os.getcwd(), "tmp_renders", request_id)
    os.makedirs(work_dir, exist_ok=True)

    try:
        response = call_llm_with_fallback(
            client,
            user_prompt=f"Create a Manim animation to explain: {promptRequest.prompt}"
        )

        if response is None:
            raise HTTPException(status_code=503, detail="No response from LLM")

        code = response.text
        cleaned_code = code.replace("```python", "").replace("```", "").strip()

        # --- SECURITY: Validate the generated code before writing/executing ---
        is_safe, reason = validate_generated_code(cleaned_code)
        if not is_safe:
            print(f"⚠️ Code validation failed: {reason}")
            raise HTTPException(status_code=400, detail=f"Generated code failed safety check: {reason}")

        # Write to a unique file in the temp directory (no race condition)
        scene_file = os.path.join(work_dir, "scene.py")
        with open(scene_file, "w", encoding="utf-8") as f:
            f.write(cleaned_code)

        match = re.search(r"class\s+(\w+)\s*\(\s*Scene\s*\):", cleaned_code)
        class_name = match.group(1) if match else "GeneratedScene"

        print(f"[{request_id}] About to start video generating for class: {class_name}")
        
        env = os.environ.copy()
        log_file = os.path.join(work_dir, "render.log")

        with open(log_file, "w") as f:
            try:
                result = subprocess.run(
                    [
                        "manim",
                        scene_file,
                        class_name,
                        "-ql",
                        "--output_file", f"{class_name}.mp4",
                        "--media_dir", os.path.join(work_dir, "media"),
                    ],
                    cwd=work_dir,
                    env=env,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    check=True,
                    start_new_session=True,
                    timeout=500
                )
            except KeyboardInterrupt:
                print("Rendering interrupted by user.")
                raise HTTPException(status_code=499, detail="User interrupted the process")
            except subprocess.CalledProcessError as e:
                print(f"[{request_id}] Render failed. Return code:", e.returncode)
                raise HTTPException(status_code=500, detail="Manim rendering failed. The generated code may have syntax errors.")

        with open(log_file, "r") as lf:
            log_contents = lf.read()
            print(f"[{request_id}] === Render Log ===")
            print(log_contents)

        print(f"[{request_id}] Completed rendering")

        output_dir = os.path.join(work_dir, "media", "videos", "scene", "480p15")
        filename = f"{class_name}.mp4"
        video_path = os.path.join(output_dir, filename)

        print(f"[{request_id}] Looking for video: {video_path}")
        print(f"[{request_id}] Exists? {os.path.exists(video_path)}")

        if not os.path.exists(video_path):
            # Try to find the video in the media directory
            for root, dirs, files in os.walk(os.path.join(work_dir, "media")):
                print(f"{root}: {files}")
                for file in files:
                    if file.endswith(".mp4"):
                        video_path = os.path.join(root, file)
                        break
            
            if not os.path.exists(video_path):
                raise HTTPException(status_code=500, detail="Video file not found after rendering")
        
        url = upload_video(video_path)

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
            raise HTTPException(status_code=500, detail="Video added failed.")

    except HTTPException:
        raise
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Rendering timed out.")
    except Exception as e:
        error_msg = str(e)
        if "All Gemini models exhausted" in error_msg:
            raise HTTPException(status_code=429, detail="All AI models are temporarily rate-limited. Please try again in a minute.")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {error_msg[:200]}")
    finally:
        # Clean up temp directory after request completes
        try:
            shutil.rmtree(work_dir, ignore_errors=True)
        except Exception:
            pass

    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr or "Rendering failed")
    
    return {"message": "✅ Video generated", "data": {"url": url}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_excludes=["tmp_renders/*", "media/*", "*.log"],
    )
