# DocuMind

AI-powered document Q&A platform built with Next.js 14, FastAPI, LangChain-ready RAG services, OpenAI/HuggingFace embedding adapters, vector-store abstraction, Redis-style caching, TypeScript, Tailwind CSS, Framer Motion, TanStack Query, and Zod.

## Highlights

- Upload PDFs, text, Markdown, or document files and query them in natural language.
- Recursive chunking preserves page and paragraph metadata for source citations.
- Local development runs with deterministic embeddings and an in-memory vector store.
- Provider interfaces are ready for OpenAI, HuggingFace, Pinecone, ChromaDB, Redis, and MongoDB-backed metadata.
- Streaming chat interface shows token-by-token responses and a citation panel with relevance scores.
- Multi-document comparison mode answers cross-document questions side by side.

## Quick Start

```bash
npm install
npm run dev:frontend
```

In a second terminal:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The frontend runs on [http://localhost:3000](http://localhost:3000) and the backend on [http://localhost:8000](http://localhost:8000).

On Windows, after installing dependencies, you can start both with:

```cmd
scripts\start-dev.cmd
```

Install production provider integrations when you need them:

```bash
cd backend
pip install -r requirements-optional.txt
```

## Environment

Copy `.env.example` to `.env.local` for the frontend and to `backend/.env` for the backend where applicable.

The app works locally without paid services. Set provider variables when moving to production integrations:

- `EMBEDDING_PROVIDER=openai` with `OPENAI_API_KEY`
- `EMBEDDING_PROVIDER=huggingface` with local sentence-transformer dependencies
- `VECTOR_STORE=chroma` or `VECTOR_STORE=pinecone`
- `REDIS_URL` for shared embedding cache
- `MONGODB_URI` for metadata persistence

## Demo Flow

1. Upload two small policy, research, or contract PDFs.
2. Ask a grounded question in the chat.
3. Open the citation panel and point to page/paragraph references.
4. Switch to comparison mode and ask how the documents differ on the same topic.

## Deployment

- Frontend: import `frontend/` into Vercel and set `NEXT_PUBLIC_API_URL` to the Render API URL.
- Backend: deploy with `render.yaml` or the `backend/Dockerfile`.
- Local Docker API: `docker compose up api redis`.
