# Hybrid RAG Video Game Character Designer Interviewer

An intelligent chatbot system that interviews users as if they are a Video Game Character Designer, using both unstructured (PDFs → Vector DB) and structured (PostgreSQL) knowledge.

## Features
- Webcam-based face authentication (OpenCV)
- Hybrid RAG: combines semantic PDF search (FAISS) and SQL (PostgreSQL)
- Multi-agent: creative, systems, and evaluator agents (async)
- FastAPI backend, modular and production-ready
- Async, fast (<5s response)

## Quickstart

### 1. Clone & Install
```bash
git clone <repo-url>
cd hibrid-chatbot
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the root:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/hybrid_rag
OPENAI_API_KEY=sk-...
OPENAI_CHAT_MODEL=gpt-3.5-turbo
VECTOR_STORE_PATH=vector_store/faiss_index.bin
```

### 3. Seed Database & Demo Data
```bash
python -m app.db.seed
```

### 3b. Build / Rebuild Vector DB (PDF ingestion)
If you changed embedding backends/models (e.g., OpenAI → local embeddings), rebuild the FAISS index:
```bash
python -m app.rag.ingest
```

### 4. Run the API
```bash
uvicorn app.main:app --reload
```


### 5. Frontend Usage

#### Static Frontend (HTML/CSS/JS)
- Minimal, framework-free UI for login and chat
- Files:
  - `frontend/login.html` — Webcam login page
  - `frontend/chat.html` — Chat interface
  - `frontend/style.css` — Styles (centered, mobile-friendly, chat bubbles)
  - `frontend/app.js` — Handles webcam, login, chat, API calls

#### How to use
1. Start the FastAPI backend (`uvicorn app.main:app --reload`)
2. Open [http://localhost:8000/](http://localhost:8000/) for login
3. After login, you’ll be redirected to `/chat-ui` for chat
4. You can also access static files directly at `/frontend/*`

#### Endpoints
- `/` — Serves `login.html`
- `/chat-ui` — Serves `chat.html`
- `/frontend` — Serves all static frontend files

#### Notes
- Auth token is stored in browser localStorage after login
- If token is missing, chat page redirects to login
- All API calls use fetch and are CORS-enabled

See docs/architecture.md for more details.

---

## Folder Structure
```
/app
  /api         # FastAPI routes
  /agents      # Multi-agent logic
  /rag         # RAG pipeline (vector, PDF, embeddings)
  /db          # SQLAlchemy models, session, seed
  /services    # Face auth, router
  main.py      # Entrypoint
/data
  /pdfs        # PDF knowledge base
/docs
  architecture.md
requirements.txt
README.md
```

## License
MIT
