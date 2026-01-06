from fastapi import APIRouter, UploadFile
from app.services.face_auth import authenticate_face

router = APIRouter()

@router.post("/login/webcam")
async def login_webcam(file: UploadFile):
    # Delegate to the shared router logic (returns token)
    from app.services.router import webcam_auth
    return await webcam_auth(file)
