from fastapi import APIRouter, HTTPException, status# type: ignore
from libs.cloudinary import upload_video

router = APIRouter()

@router.post("/upload")
async def handle_upload():
    
    try:
        with open("classname.txt", "r") as f:
            class_name = f.readline().strip()
        url =  upload_video(rf"C:\Users\varsh\Desktop\2D-animations-video\backend\media\videos\generated_scene\480p15\{class_name}.mp4")
        return {"data": {"url": url}}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
