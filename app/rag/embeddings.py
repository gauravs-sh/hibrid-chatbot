import os
from typing import List
from dotenv import load_dotenv
load_dotenv()

EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", "local")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

if EMBEDDING_BACKEND == "local":
    from sentence_transformers import SentenceTransformer
    _st_model = SentenceTransformer(EMBEDDING_MODEL)
    async def get_embedding(text: str, model: str = None) -> List[float]:
        # SentenceTransformers is not async, so run in thread
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: _st_model.encode(text).tolist())

    async def get_embeddings(texts: list, model: str = None) -> list:
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: _st_model.encode(texts).tolist())
else:
    from openai import AsyncOpenAI
    LLM_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL")
    client = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL) if LLM_BASE_URL else AsyncOpenAI(api_key=LLM_API_KEY)
    def get_default_embedding_model():
        return os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    async def get_embedding(text: str, model: str = None) -> List[float]:
        model = model or get_default_embedding_model()
        response = await client.embeddings.create(
            input=text,
            model=model
        )
        return response.data[0].embedding
    async def get_embeddings(texts: list, model: str = None) -> list:
        model = model or get_default_embedding_model()
        embeddings = []
        for text in texts:
            emb = await get_embedding(text, model)
            embeddings.append(emb)
        return embeddings
