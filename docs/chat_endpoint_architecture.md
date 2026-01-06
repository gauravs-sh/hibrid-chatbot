# /api/chat endpoint architecture

> This is an “architecture image” using Mermaid (renders in VS Code + GitHub).

## High-level flow (components)

```mermaid
flowchart TD
  Client[Client / Postman] -->|POST /api/login/webcam (image)| AuthAPI[Auth API]
  AuthAPI --> Face[Face detection (OpenCV)]
  Face -->|token| Client

  Client -->|POST /api/chat\nHeader: token\nBody: {query}| ChatAPI[/Chat API: /api/chat/]

  ChatAPI -->|Depends(require_auth)| AuthGate[Auth gate\n(in-memory token set)]

  ChatAPI -->|probe embedding dim| Embed[get_embedding("dimension_probe")\nSentenceTransformers (local)\nor remote embeddings]
  ChatAPI -->|ensure_dim(d)| VS[FAISS Vector Store\n(load + dim sync)]

  ChatAPI --> Parallel{{Run in parallel}}

  Parallel --> Creative[CreativeGameDesignAgent]
  Creative -->|get_embedding(query)| Embed
  Creative -->|vector search| VS
  Creative -->|LLM call (optional)| LLM[(OpenAI-compatible LLM)]
  Creative -->|fallback if LLM fails| Creative

  Parallel --> Systems[SystemsAgent]
  Systems -->|SQL queries by keyword| DB[(Postgres/Supabase)]
  Systems -->|LLM call (optional)| LLM
  Systems -->|fallback if LLM fails| Systems

  Creative --> Eval[EvaluatorAgent]
  Systems --> Eval
  Eval -->|LLM merge (optional)| LLM
  Eval -->|fallback merge if LLM fails| Eval

  Eval -->|JSON: answer, creative, systems| Client
```

## Runtime sequence (what happens per request)

```mermaid
sequenceDiagram
  autonumber
  participant C as Client
  participant Chat as /api/chat
  participant Auth as require_auth(token)
  participant Emb as get_embedding()
  participant VS as FAISS vector_store
  participant Cr as CreativeAgent
  participant Sy as SystemsAgent
  participant DB as Postgres/Supabase
  participant Ev as EvaluatorAgent
  participant LLM as LLM (optional)

  C->>Chat: POST /api/chat (token + query)
  Chat->>Auth: validate token
  Auth-->>Chat: ok

  Chat->>Emb: embedding("dimension_probe")
  Emb-->>Chat: vector[d]
  Chat->>VS: ensure_dim(d)

  par Creative + Systems in parallel
    Chat->>Cr: answer(query)
    Cr->>Emb: embedding(query)
    Emb-->>Cr: vector[d]
    Cr->>VS: search(vector)
    VS-->>Cr: top_k docs (maybe empty)
    Cr->>LLM: chat completion (optional)
    LLM-->>Cr: response OR error
    Cr-->>Chat: creative_answer (LLM or fallback)

    Chat->>Sy: answer(query)
    Sy->>DB: SELECT table based on keywords
    DB-->>Sy: rows
    Sy->>LLM: chat completion (optional)
    LLM-->>Sy: response OR error
    Sy-->>Chat: systems_answer (LLM or fallback)
  end

  Chat->>Ev: evaluate(query, creative_answer, systems_answer)
  Ev->>LLM: merge/choose (optional)
  LLM-->>Ev: merged answer OR error
  Ev-->>Chat: final_answer (LLM or fallback)

  Chat-->>C: {answer, creative, systems}
```

## Notes (why you sometimes see “LLM fallback”)

- If the LLM call fails (missing key, quota/429, provider down), each agent returns a deterministic fallback string.
- In your current handler, if the Creative agent throws an exception before its internal fallback, `/api/chat` sets `creative` to an empty string.
