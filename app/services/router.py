from fastapi import APIRouter, UploadFile, HTTPException, status, Depends
from app.services.face_auth import authenticate_face

router = APIRouter()

authenticated_users = set()

@router.post("/auth/webcam")
async def webcam_auth(file: UploadFile):
    import secrets
    is_face = await authenticate_face(file)
    if not is_face:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No face detected. Access denied.")
    # Generate a simple token
    token = secrets.token_urlsafe(16)
    authenticated_users.add(token)
    return {"authenticated": True, "token": token}

from fastapi import Header
def require_auth(token: str = Header(...)):
    if token not in authenticated_users:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
