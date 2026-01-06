import asyncio
import os
from app.rag.pdf_loader import load_and_chunk_pdfs
from app.rag.embeddings import get_embeddings
from app.rag.vector_store import FaissVectorStore


async def ingest_pdfs(
    pdf_folder: str = "data/pdfs",
    chunk_size: int = 500,
    overlap: int = 50,
) -> None:
    chunks = load_and_chunk_pdfs(pdf_folder, chunk_size=chunk_size, overlap=overlap)
    if not chunks:
        print(f"No PDF chunks found in {pdf_folder}")
        return

    texts = [c["text"] for c in chunks]
    embeddings = await get_embeddings(texts)
    if not embeddings:
        print("No embeddings generated.")
        return

    dim = len(embeddings[0])
    store = FaissVectorStore(dim=dim)
    store.add(
        embeddings,
        [
            {
                "filename": c["filename"],
                "chunk_id": c["chunk_id"],
                "text": c["text"],
            }
            for c in chunks
        ],
    )
    store.save()
    print(f"Ingested {len(chunks)} chunks into FAISS (dim={dim}).")


async def main() -> None:
    pdf_folder = os.getenv("PDF_FOLDER", "data/pdfs")
    await ingest_pdfs(pdf_folder=pdf_folder)


if __name__ == "__main__":
    asyncio.run(main())
