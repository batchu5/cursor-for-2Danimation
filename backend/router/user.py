from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import List, Optional
from configurations import user_collection
from middleware import get_current_user_id
from datetime import datetime
from collections import defaultdict

userRouter = APIRouter()


class Video(BaseModel):
    prompt: str
    url: str
    conversationId: str


class AddVideoRequest(BaseModel):
    user_id: str
    prompt: str
    url: str


@userRouter.post("/auth/callback")
def auth_callback(user_id: str = Depends(get_current_user_id), request: Request = None):
    """
    Called by the frontend after Auth0 login to upsert the user in MongoDB.
    Uses the Auth0 'sub' claim as the user identifier.
    """
    # Try to get user info from request body (frontend sends name, email, picture)
    import json
    body = {}
    try:
        import asyncio
        # For sync endpoint, we read the body differently
        pass
    except Exception:
        pass

    # Check if user already exists by Auth0 sub
    existing_user = user_collection.find_one({"auth0_id": user_id})

    if not existing_user:
        # Create new user with Auth0 sub as identifier
        user_data = {
            "auth0_id": user_id,
            "videos": [],
            "created_at": datetime.utcnow(),
        }
        user_collection.insert_one(user_data)
        return {"message": "User created", "auth0_id": user_id}

    return {"message": "User exists", "auth0_id": user_id}


@userRouter.post("/auth/sync")
async def auth_sync(request: Request, user_id: str = Depends(get_current_user_id)):
    """
    Sync Auth0 user profile info (name, email, picture) to MongoDB.
    Called after login to keep profile data up-to-date.
    """
    body = await request.json()
    name = body.get("name", "")
    email = body.get("email", "")
    picture = body.get("picture", "")

    user_collection.update_one(
        {"auth0_id": user_id},
        {
            "$set": {
                "username": email,
                "name": name,
                "picture": picture,
                "updated_at": datetime.utcnow(),
            },
            "$setOnInsert": {
                "auth0_id": user_id,
                "videos": [],
                "created_at": datetime.utcnow(),
            },
        },
        upsert=True,
    )

    return {"message": "User synced", "auth0_id": user_id}


@userRouter.get("/userInfo")
def user_information(user_id: str = Depends(get_current_user_id)):
    user = user_collection.find_one({"auth0_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    name = user.get("name", user.get("username", ""))
    picture = user.get("picture", "")

    return {"name": name, "picture": picture}


@userRouter.post("/addVideo")
def add_video(req: Video, user_id: str = Depends(get_current_user_id)):
    conversation_id = req.conversationId
    print(conversation_id)
    video_data = {"prompt": req.prompt, "url": req.url, "conversationId": conversation_id}
    result = user_collection.update_one(
        {"auth0_id": user_id},
        {"$push": {"videos": video_data}},
    )
    if result.modified_count == 1:
        return {"message": "Video added successfully", "conversationId": conversation_id}
    raise HTTPException(status_code=400, detail="User not found or update failed")


@userRouter.get("/myVideos")
def get_user_videos(user_id: str = Depends(get_current_user_id)):
    user = user_collection.find_one({"auth0_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"videos": user.get("videos", [])}


@userRouter.get("/grouped_by_conversation")
async def get_grouped_videos(user_id: str = Depends(get_current_user_id)):
    user = user_collection.find_one({"auth0_id": user_id})
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
        sorted_videos = sorted(videos, key=lambda v: v.get("timestamp", datetime.min))
        result.append(sorted_videos)

    return result[::-1]
