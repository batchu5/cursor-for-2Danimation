from middleware import get_current_user_id
from fastapi import Depends
from fastapi import APIRouter, HTTPException, status # type: ignore
from libs.cloudinary import upload_video
import os

router = APIRouter()

@router.post("/upload")
async def handle_upload(user_id: str = Depends(get_current_user_id)):
    """Upload endpoint — requires authentication."""
    try:
        with open("classname.txt", "r") as f:
            class_name = f.readline().strip()

        BASE_DIR = os.getcwd()
        video_path = os.path.join(BASE_DIR, "media", "videos", "generated_scene", "480p15", f"{class_name}.mp4")

        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video file not found")

        url = upload_video(video_path)
        return {"data": {"url": url}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
