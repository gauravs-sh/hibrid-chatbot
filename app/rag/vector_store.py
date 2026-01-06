import os
import faiss
import numpy as np
import pickle
import logging
from typing import List, Dict, Any, Optional

VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "vector_store/faiss_index.bin")
META_STORE_PATH = os.getenv("META_STORE_PATH", "vector_store/meta.pkl")

class FaissVectorStore:
    def __init__(self, dim: Optional[int]):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim) if dim is not None else None
        self.meta: List[Dict[str, Any]] = []

    def ensure_dim(self, dim: int, *, reset: bool = False) -> None:
        """Ensure the underlying FAISS index has the expected dimensionality.

        If an existing index has a different dim (common after switching embedding models),
        we reset to a fresh empty index to prevent runtime assertion errors.
        """
        if self.index is None or reset:
            self.dim = dim
            self.index = faiss.IndexFlatL2(dim)
            self.meta = []
            return

        current_dim = getattr(self.index, "d", self.dim)
        if current_dim != dim:
            logging.warning(
                "FAISS dim mismatch (index=%s, query=%s). Resetting vector store.",
                current_dim,
                dim,
            )
            self.dim = dim
            self.index = faiss.IndexFlatL2(dim)
            self.meta = []

    def add(self, embeddings: List[List[float]], metadatas: List[Dict[str, Any]]):
        if not embeddings:
            return
        self.ensure_dim(len(embeddings[0]))
        arr = np.array(embeddings).astype('float32')
        self.index.add(arr)
        self.meta.extend(metadatas)

    def search(self, query_emb: List[float], top_k: int = 5):
        if self.index is None:
            self.ensure_dim(len(query_emb))
            return []

        if len(query_emb) != getattr(self.index, "d", self.dim):
            # Reset to avoid faiss assertion crash; caller should re-ingest.
            self.ensure_dim(len(query_emb), reset=True)
            return []

        arr = np.array([query_emb]).astype('float32')
        _, I = self.index.search(arr, top_k)
        results = []
        for idx in I[0]:
            if idx < len(self.meta):
                results.append(self.meta[idx])
        return results

    def save(self):
        if self.index is None:
            return
        os.makedirs(os.path.dirname(VECTOR_STORE_PATH), exist_ok=True)
        faiss.write_index(self.index, VECTOR_STORE_PATH)
        with open(META_STORE_PATH, 'wb') as f:
            pickle.dump(self.meta, f)

    def load(self):
        if os.path.exists(VECTOR_STORE_PATH):
            self.index = faiss.read_index(VECTOR_STORE_PATH)
            self.dim = getattr(self.index, "d", self.dim)
        if os.path.exists(META_STORE_PATH):
            with open(META_STORE_PATH, 'rb') as f:
                self.meta = pickle.load(f)
