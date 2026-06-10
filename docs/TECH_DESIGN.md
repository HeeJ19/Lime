# Technical Design Document: Lime MVP

## Executive Summary

**System:** Lime
**Architecture Pattern:** Monolithic Frontend (Next.js) + Decoupled AI Microservice (FastAPI)
**Estimated Effort:** 4 weeks

## Architecture Overview

### High-Level Architecture
* **Frontend/Router:** Next.js (hosted on Vercel) serves the React UI and handles authentication and routing.
* **AI Service:** Python (FastAPI) handles the heavy-lifting: background removal (`briaai/RMBG-1.4`) and VLM tagging (Gemini 2.5 Flash).
* **Database/Auth:** Supabase (PostgreSQL for metadata, Supabase Auth for users).
* **Vector Search:** Pinecone (Starter tier) stores the high-dimensional embeddings for your outfit recommendation engine.

### Tech Stack Decisions
| Layer | Tool | Rationale |
| :--- | :--- | :--- |
| **Frontend** | Next.js (App Router) | Best-in-class developer experience, Vercel native. |
| **Backend** | Python (FastAPI) | Your comfort zone; essential for ML pipeline efficiency. |
| **Database/Auth** | Supabase | Simplifies Auth + Postgres; generous free tier. |
| **Vector DB** | Pinecone | Managed service, $0 starter tier, easy Python/JS integration. |
| **AI Strategy** | Cursor / Claude Code | Allows high-agency development while bridging your learning curve. |

---

## Component Design

### Frontend (Next.js)
* **Auth:** Use `@supabase/auth-helpers-nextjs` for server-side auth protection.
* **UI:** Tailwind CSS + Shadcn/ui (for fast, high-end streetwear components).
* **Swiping Interface:** Implement using `framer-motion` for smooth, Tinder-style gestures.

### AI Backend (FastAPI)
* **Pipeline:**
  1. Receive image blob from Next.js via POST.
  2. Perform background removal using local `RMBG-1.4`.
  3. Send stripped image to Gemini 2.5 Flash for JSON tag generation.
  4. Convert tags to vectors and upsert into Pinecone.
  5. Return metadata to the frontend.

---

## Feature Implementation

### 1. Ingestion & Tagging
* **Flow:** Next.js `Server Action` uploads the file -> FastAPI endpoint -> Background Removal -> VLM Tagging -> JSON output -> Pinecone embedding storage.
* **Success Criteria:** JSON metadata must be validated with Pydantic in Python before hitting the database.

### 2. Tinder-Style Swiping
* **Flow:** Next.js queries Pinecone/Postgres based on weather (Open-Meteo) -> Returns distinct categories (Tops, Bottoms, Shoes) -> `framer-motion` cards handle swipe events.

---

## Security & Scalability

* **Data Sensitivity:** Clothing photos are stored as public/private assets; use Supabase Storage with Row Level Security (RLS) enabled.
* **Performance:** Use `dynamic` imports in Next.js for the heavy swiping components to ensure fast initial page loads.
* **Auth:** Supabase provides built-in rate-limiting and JWT security for free.

---

## AI-Assisted Development Workflow

* **Cursor:** Use Cursor as your primary IDE to bridge the Python-to-Next.js gap. It will allow you to highlight Python backend code and ask for equivalent TypeScript implementation in your Next.js components.
* **Claude Code:** Use this when you have architectural questions that require multi-file context analysis.

---

## Cost Analysis

| Service | Tier | Cost |
| :--- | :--- | :--- |
| **Vercel** | Hobby | $0 |
| **Supabase** | Free | $0 |
| **Pinecone** | Starter | $0 |
| **Gemini API** | Free | $0 |
| **Total** | | **$0.00/month** |
