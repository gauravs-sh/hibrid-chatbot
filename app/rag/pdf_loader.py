import os
from PyPDF2 import PdfReader
from tqdm import tqdm

def load_pdfs_from_folder(folder_path: str):
    pdf_texts = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            text = ""
            try:
                reader = PdfReader(file_path)
                for page in reader.pages:
                    text += page.extract_text() or ""
            except Exception:
                # Fallback for non-standard or placeholder "pdf" files during demos
                try:
                    with open(file_path, "rb") as f:
                        text = f.read().decode("utf-8", errors="ignore")
                except Exception:
                    text = ""
            pdf_texts.append({"filename": filename, "text": text})
    return pdf_texts

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i+chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def load_and_chunk_pdfs(folder_path: str, chunk_size: int = 500, overlap: int = 50):
    pdfs = load_pdfs_from_folder(folder_path)
    all_chunks = []
    for pdf in tqdm(pdfs, desc="Chunking PDFs"):
        chunks = chunk_text(pdf["text"], chunk_size, overlap)
        for idx, chunk in enumerate(chunks):
            all_chunks.append({
                "filename": pdf["filename"],
                "chunk_id": idx,
                "text": chunk
            })
    return all_chunks
