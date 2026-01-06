import cv2
import numpy as np
import tempfile
from fastapi import UploadFile

HAAR_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)

def detect_face_from_image(image_bytes: bytes) -> bool:
    # Convert bytes to numpy array
    npimg = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    if img is None:
        return False
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    return len(faces) > 0

async def authenticate_face(file: UploadFile) -> bool:
    image_bytes = await file.read()
    return detect_face_from_image(image_bytes)
