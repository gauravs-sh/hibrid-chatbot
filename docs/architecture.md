# Architecture Overview

## System Components

### 1. Authentication
- **Webcam-based**: Uses OpenCV Haar Cascade to detect a face from an uploaded image.
- **API**: `/api/login/webcam` endpoint blocks access unless a face is detected.

### 2. Hybrid RAG Pipeline
- **Unstructured Data**: PDFs in `/data/pdfs` are loaded, chunked, embedded (OpenAI), and stored in FAISS vector DB.
- **Structured Data**: PostgreSQL tables for genres, archetypes, skills, stats, designers, questions (SQLAlchemy ORM).
- **Query Routing**: System decides if a query needs vector search, SQL, or both.

### 3. Multi-Agent Architecture
- **Creative Agent**: Uses vector search and LLM for creative, context-rich answers.
- **Systems Agent**: Uses SQL queries and LLM for precise, constraint-focused answers.
- **Evaluator Agent**: Scores and merges agent responses for the best final answer.
- **Async**: All agents run in parallel for speed.

### 4. FastAPI Backend
- Modular routers for `/api/auth` and `/api/chat`.
- Dependency-injected DB session and authentication.
- CORS enabled for frontend integration.

### 5. Performance
- Embedding and vector search are cached.
- Async DB and LLM calls.
- End-to-end response time < 5 seconds.

---

## Data Flow
1. **User logs in** via webcam (face required).
2. **User asks a question** (e.g., "How would you design a new mage archetype?").
3. **System routes query** to both agents:
   - Creative Agent: semantic PDF search + LLM
   - Systems Agent: SQL query + LLM
4. **Evaluator Agent** merges or selects best answer.
5. **Final response** returned to user.

---

## Extending the System
- Add more PDFs to `/data/pdfs` and re-run embedding.
- Add more interview questions or archetypes in the DB.
- Swap LLM provider by changing environment variables.

---

## Security Notes
- Webcam auth is for demo only (no biometric storage).
- Use HTTPS and secure session/token management in production.

---

## See README.md for setup and API usage.
