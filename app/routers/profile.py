from fastapi import APIRouter, UploadFile, File
from app.services.minio_service import upload_profile_picture

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)

@router.post("/upload-picture")
async def upload_picture(file: UploadFile = File(...)):
    file_url = upload_profile_picture(file.file, file.filename)  # pass file.file instead of reading
    return {"file_url": file_url}
