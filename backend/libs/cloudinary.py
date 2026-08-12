import cloudinary
import os
from cloudinary.uploader import upload# type: ignore
from fastapi import HTTPException, status# type: ignore
from dotenv import load_dotenv# type: ignore

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def upload_video(video_path: str) -> str:
    try:
        with open(video_path, "rb") as video_file:
            upload_result = upload(video_file, resource_type="video")
            return upload_result["secure_url"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading video: {e}"
        )
