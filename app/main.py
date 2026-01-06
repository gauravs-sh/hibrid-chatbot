import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, chat
from app.services.router import router as auth_router

app = FastAPI(title="Hybrid RAG Video Game Character Designer Interviewer")

# CORS (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(auth_router, prefix="/api", tags=["internal-auth"])

@app.get("/")
def root():
    return {"msg": "Hybrid RAG Video Game Character Designer Interviewer API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
