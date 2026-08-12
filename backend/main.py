from dotenv import load_dotenv #type: ignore
import os
import subprocess
import sys
from fastapi import FastAPI, HTTPException # type: ignore
import re
from router.user import userRouter
from openai import OpenAI # type: ignore
from fastapi.middleware.cors import CORSMiddleware
from libs.cloudinary import upload_video
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel,Field
from middleware import get_current_user_id
import subprocess
from bson import ObjectId
from fastapi import Depends
from configurations import user_collection
import sys
import glob
from datetime import datetime

import shutil
from starlette.middleware.sessions import SessionMiddleware
manim_path = shutil.which("manim")

class PromptRequest(BaseModel):
    prompt: str
    conversationId: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

app = FastAPI()
origins = [
     "https://cursor-for-2-danimation.vercel.app",
     "http://localhost:5173"
]
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "super-secret-key"))
app.include_router(userRouter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            
    allow_credentials=True,
    allow_methods=["*"],              
    allow_headers=["*"],              
)
   
@app.post("/generate_video")
async def generate_video(promptRequest: PromptRequest, user_id: str = Depends(get_current_user_id)):
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=[{"role":"user","content":f"You are a Manim expert. Return only valid Manim Community Edition Python code. Do not include any explanations or comments. I want just the code block, nothing else. Avoid using any external libraries like scipy, numpy, or networkx. Use only core Manim features. Keep the code minimal, with one class .Add import statment for manim. Now create a Manim animation to explain {promptRequest.prompt}."}]
        )

        if(response == None):
            return {"error" : "No response"}
        

        code = response.choices[0].message.content
        cleaned_code = code.replace("```python", "").replace("```", "").strip()

        with open("generated_scene.py", "w", encoding="utf-8") as f:
            f.write(cleaned_code);
        match = re.search(r"class\s+(\w+)\s*\(\s*Scene\s*\):", cleaned_code)

        class_name = match.group(1) if match else "GeneratedScene"
        # class_name="HelloScene"
        with open("classname.txt", "w") as f:
            f.write(class_name);
        
        print("About to start video generating...")
        
        env = os.environ.copy()  
        BASE_DIR = os.getcwd()

        with open("render.log", "w") as f:
            try :
                result = subprocess.run(
                    [
                        "manim",
                        "generated_scene.py",
                        class_name,
                        "-ql",
                        "--output_file", f"{class_name}.mp4",
                    ],
                    cwd=BASE_DIR,
                    env=env,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    check=True,
                    start_new_session=True,
                    timeout=500
                )
            except KeyboardInterrupt:
                print("Rendering interrupted by user.")
                return {"return code": 130, "output": "User interrupted the process"}
            except subprocess.CalledProcessError as e:
                print("Return code:", e.returncode)

        with open("render.log", "r") as log_file:
            log_contents = log_file.read()
            print("=== Render Log ===")
            print(log_contents)

        print("fuck it completed the generate_scene.py")

        
        output_dir = os.path.join(BASE_DIR, "media", "videos", "generated_scene", "480p15")
        os.makedirs(output_dir, exist_ok=True)
        
        class_name = class_name
        filename = f"{class_name}.mp4"
        video_path = os.path.join(output_dir, filename)

        print("BASE_DIR:", BASE_DIR)
        print("Output dir:", output_dir)
        print("Looking for video:", video_path)
        print("does video path exist", os.path.exists(video_path));
        print("Exists?", os.path.exists(video_path))
        

        if not os.path.exists(video_path):
            print("Directory contents:")
            for root, dirs, files in os.walk(os.path.join(BASE_DIR, "media")):
                print(f"{root}: {files}")
            return {"error": f"Video file not found at {video_path}"}
        
        url = upload_video(video_path)

        video_data = {"prompt": promptRequest.prompt, "url": url, "conversationId": promptRequest.conversationId,"timestamp": promptRequest.timestamp}
        update_result = user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {"videos": video_data}}
        )

        if update_result.modified_count != 1:
            raise HTTPException(status_code=500, detail="Video added failed.")
    except subprocess.TimeoutExpired:
        return {"error": "Rendering timed out."}

    if result.returncode != 0:
        return {"error": result.stderr}
    
    return {"message": "✅ Video generated" , "data" : {"url": url}};
