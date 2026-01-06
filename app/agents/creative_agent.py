import asyncio
from app.rag.vector_store import FaissVectorStore
from app.rag.embeddings import get_embedding
from app.rag.pdf_loader import chunk_text
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()


class CreativeGameDesignAgent:
    def __init__(self, vector_store: FaissVectorStore, embedding_dim: int = 1536):
        self.vector_store = vector_store
        self.embedding_dim = embedding_dim
        from dotenv import load_dotenv
        load_dotenv()
        import os
        LLM_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        LLM_BASE_URL = os.getenv("LLM_BASE_URL")
        self.llm = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL) if LLM_BASE_URL else AsyncOpenAI(api_key=LLM_API_KEY)

    async def answer(self, query: str) -> str:
        # Embed query
        query_emb = await get_embedding(query)
        # Vector search
        docs = self.vector_store.search(query_emb, top_k=5)
        context = "\n".join([d['text'] for d in docs])
        # LLM prompt
        prompt = f"You are a creative video game character designer. Use the following context to answer the interview question as creatively as possible.\nContext:\n{context}\nQuestion: {query}"
        try:
            response = await self.llm.chat.completions.create(
                model=os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "You are a creative game designer."},
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content.strip()
        except Exception:
            # Deterministic fallback (no external LLM)
            base = [
                "Creative answer (LLM fallback):",
                f"Question: {query}",
                "",
                "Inspiration from PDFs:",
                context or "(no vector context available yet — run `python -m app.rag.ingest`)" ,
                "",
                "Pitch:",
                "I’d anchor the character around a strong silhouette + readable combat loop, then express their fantasy through 2–3 signature abilities, "
                "a branching skill tree choice, and a clear weakness that invites build variety.",
            ]
            return "\n".join(base)
