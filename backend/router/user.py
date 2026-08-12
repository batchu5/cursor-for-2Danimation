
from fastapi import APIRouter,HTTPException,Request # type: ignore
from pydantic import BaseModel# type: ignore
from typing import List, Optional
from bson import ObjectId #type : ignore
from configurations import user_collection
userRouter = APIRouter()
from fastapi import Response
from auth import create_access_token
from middleware import get_current_user_id
from fastapi import Depends
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse
from jose import jwt
from dotenv import load_dotenv
from uuid import uuid4
from datetime import datetime
from collections import defaultdict
import os
load_dotenv()

oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile', 'prompt':'consent'}
)



class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class Video(BaseModel):
    prompt: str
    url: str
    conversationId: str

class User(BaseModel):
    username: str
    password: str
    picture: str
    videos: Optional[List[Video]] = []

class LoginRequest(BaseModel):
    username: str
    password: str

class AddVideoRequest(BaseModel):
    user_id: str
    prompt: str
    url: str

@userRouter.get("/login/google")
async def login_google(request: Request):
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@userRouter.get("/auth/google")
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")
    email = user_info.get("email")
    name = user_info.get("name")  
    picture = user_info.get("picture")  
    existing_user = user_collection.find_one({"username": email})
    if not existing_user:
        user_data = {"username": email, "name": name, "password": None, "picture": picture}
        result = user_collection.insert_one(user_data)
        user_id = result.inserted_id
    else:
        user_id = existing_user["_id"]
    access_token = create_access_token({"user_id": str(user_id)})
    response = RedirectResponse(url="https://cursor-for-2-danimation.vercel.app/dashboard")
    response.set_cookie(
        key="token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="none"
    )
    return response

@userRouter.get("/userInfo")
def userInformation(user_id: str = Depends(get_current_user_id)):
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    name = user.get("username", "")
    picture = user.get("picture", "")

    return {"name": name, "picture": picture}


@userRouter.post("/signup")
def signup(user: User):
    existing_user = user_collection.find_one({"username": user.username.strip().lower()})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    user_dict = user.model_dump()
    user_dict["username"] = user.username.strip().lower()
    result = user_collection.insert_one(user_dict)
    return {"message": "User created", "user_id": str(result.inserted_id)}

@userRouter.post("/signin")
def signin(login: LoginRequest, response: Response):
    user = user_collection.find_one({
        "username": login.username.strip().lower(),
        "password": login.password  
    })

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"user_id": str(user["_id"])})

    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
    )

    return {"message": "Login successful", "user_id": str(user["_id"])}

@userRouter.post("/addVideo")
def add_video(req: Video, user_id: str = Depends(get_current_user_id)):
    conversation_id = req.conversationId
    print(conversation_id);
    video_data = {"prompt": req.prompt, "url": req.url, "conversationId": conversation_id}
    result = user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"videos": video_data}}
    )
    if result.modified_count == 1:
        return {"message": "Video added successfully", "conversationId": conversation_id }
    return {"error": "User not found or update failed"}

@userRouter.get("/myVideos")
def get_user_videos(user_id: str = Depends(get_current_user_id)):
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "videos": user.get("videos", [])
    }

@userRouter.get("/grouped_by_conversation")
async def get_grouped_videos(user_id: str = Depends(get_current_user_id)):
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_videos = user.get("videos", [])

    # Group videos by conversationId
    grouped_by_conversation = {}
    for video in user_videos:
        conv_id = video.get("conversationId")
        if conv_id:
            grouped_by_conversation.setdefault(conv_id, []).append(video)

    # Sort videos inside each group by timestamp (oldest first)
    result = []
    for conv_id, videos in grouped_by_conversation.items():
        sorted_videos = sorted(videos, key=lambda v: v["timestamp"])
        result.append(sorted_videos)
    # result.sort(key=lambda group: group["videos"][-1]["timestamp"], reverse=True)

    return result[::-1]

# @userRouter.post("/logout")
# def logout(response: Response):
#     response.delete_cookie("access_token")
#     return {"message": "Logged out"}
