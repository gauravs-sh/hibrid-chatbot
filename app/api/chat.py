import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.services.router import require_auth
from app.db.session import get_db
from app.rag.vector_store import FaissVectorStore
from app.rag.embeddings import get_embedding
from app.agents.creative_agent import CreativeGameDesignAgent
from app.agents.systems_agent import SystemsAgent
from app.agents.evaluator_agent import EvaluatorAgent
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

# Load vector store at startup (singleton)
vector_store = FaissVectorStore(dim=None)
vector_store.load()

evaluator = EvaluatorAgent()

class ChatRequest(BaseModel):
    query: str

from fastapi import Header

@router.post("/chat")
async def chat_endpoint(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    token: str = Header(...),
    _auth=Depends(require_auth)
):
    # Ensure vector store dimension matches the current embedding backend/model.
    # If the existing FAISS index was created with a different embedding model,
    # this will safely reset the index (empty) instead of crashing.
    try:
        probe = await get_embedding("dimension_probe")
        vector_store.ensure_dim(len(probe))
    except Exception:
        # If embeddings fail, we can still answer via the SystemsAgent.
        pass

    creative_agent = CreativeGameDesignAgent(vector_store)
    systems_agent = SystemsAgent(db)
    # Run both agents in parallel
    creative_task = asyncio.create_task(creative_agent.answer(req.query))
    systems_task = asyncio.create_task(systems_agent.answer(req.query))
    creative_answer, systems_answer = await asyncio.gather(
        creative_task,
        systems_task,
        return_exceptions=True,
    )

    if isinstance(creative_answer, Exception):
        creative_answer = ""
    if isinstance(systems_answer, Exception):
        systems_answer = "Systems agent failed; returning fallback response."
    # Evaluate/merge
    final_answer = await evaluator.evaluate(req.query, creative_answer, systems_answer)
    return {"answer": final_answer, "creative": creative_answer, "systems": systems_answer}
