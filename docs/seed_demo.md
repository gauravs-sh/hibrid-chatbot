# Seed & Demo Data Instructions

## 1. Seed the Database

Ensure your PostgreSQL server is running and the DATABASE_URL is set in your .env file (see README for details).

Run the following command to create tables and seed example data:

```bash
python -m app.db.seed
```

## 2. Ingest Example PDF

The example PDF is already placed in `/data/pdfs/character_design_principles.pdf`.

To ingest and embed PDFs, use the RAG pipeline (see docs/architecture.md for details).

---

You are now ready to run the Hybrid RAG system with demo data!
