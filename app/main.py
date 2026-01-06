import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, chat
from app.services.router import router as auth_router


from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Hybrid RAG Video Game Character Designer Interviewer")

# CORS (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount /frontend as static directory
frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")

# Routers
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(auth_router, prefix="/api", tags=["internal-auth"])


# Serve login.html at /
@app.get("/", include_in_schema=False)
async def serve_login():
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(frontend_path, "login.html"))

# Serve chat.html at /chat-ui
@app.get("/chat-ui", include_in_schema=False)
async def serve_chat():
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(frontend_path, "chat.html"))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
