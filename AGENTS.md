# AGENTS.md — Master Plan for Lime

## Project Overview & Stack
**App:** Lime
**Overview:** Lime is an AI-powered digital wardrobe app. A user snaps a photo of a clothing item; the backend strips the background and uses a vision-language model (VLM) to auto-tag it (silhouette, palette, texture, aesthetic). Items are converted to vector embeddings so Lime can recommend weather-aware, aesthetically-coherent outfits through a Tinder-style swiping interface — no manual cataloging, no rigid if/then matching rules like competitors (Indyx, Acloset, Whering).
**Stack:** Next.js (App Router, React, Tailwind CSS + Shadcn/ui, framer-motion) on Vercel; Python FastAPI AI microservice (`briaai/RMBG-1.4` background removal + Gemini 2.5 Flash VLM tagging); Supabase (Postgres + Auth + Storage with RLS); Pinecone (vector search); Open-Meteo (weather).
**Critical Constraints:**
- **Strict $0/month budget** — only free tiers: Vercel Hobby, Supabase Free, Pinecone Starter, Gemini 2.5 Flash free tier, Open-Meteo (no key required).
- **4-week MVP sprint** — keep scope to the three must-have features below; do not build anything from "Future Features."
- **Mobile-first** — the swiping deck must feel smooth on mobile viewports; no animation lag.
- **Reliable JSON contract** — Gemini's tag output must be valid JSON, validated with Pydantic before it touches the database. Broken JSON parsing is an explicit non-acceptance criterion in the PRD.

## Setup & Commands
Execute these for standard workflows. Do not invent new package manager or runtime commands.
- **Frontend setup:** `cd frontend && npm install`
- **Frontend dev:** `cd frontend && npm run dev`
- **Frontend lint:** `cd frontend && npm run lint`
- **Frontend build:** `cd frontend && npm run build`
- **Frontend test:** `cd frontend && npm test` *(no test runner installed yet — add one, e.g. Vitest, when the first component lands)*
- **Backend setup:** `cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- **Backend dev:** `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload`
- **Backend test:** `cd backend && source .venv/bin/activate && pytest` *(no tests written yet — add `pytest` to requirements.txt and write the first one alongside the ingestion pipeline)*

> **Framework version note:** The installed Next.js in `frontend/` may have breaking changes vs. training data — APIs, conventions, and file structure can differ. Check `frontend/node_modules/next/dist/docs/` and heed deprecation notices before writing Next.js code.

## Protected Areas
Do NOT modify these without explicit human approval:
- **Infrastructure:** Vercel project config, FastAPI hosting config (Render/Hugging Face Spaces), `.github/workflows/`.
- **Database Migrations:** Supabase Postgres migrations and Row Level Security (RLS) policies on Storage/tables.
- **Third-Party Integrations:** Supabase Auth setup, Pinecone index configuration, Gemini/Pinecone/Supabase API keys and `.env` files.

## Coding Conventions
- **Formatting:** Enforce ESLint/Prettier on the frontend and `ruff`/`black` on the backend. No warnings in new code.
- **Architecture rules:** Keep the Next.js app a thin UI/routing layer. Keep all ML/vision logic (background removal, VLM tagging, embedding generation) inside the FastAPI service. Don't blur this boundary — see `agent_docs/code_patterns.md`.
- **Testing expectations:** Pydantic models for every VLM JSON contract; unit tests for tagging/embedding utilities; integration tests for the upload→tag→embed→store pipeline and the weather→recommendation query.
- **Type Safety:** Strict TypeScript on the frontend (no `any`); typed Pydantic models on the backend.

## Agent Behaviors
These rules apply across all AI coding assistants:
1. **Plan Before Execution:** ALWAYS propose a brief step-by-step plan before changing more than one file, and wait for approval.
2. **Refactor Over Rewrite:** Prefer incremental refactors over rewriting large blocks.
3. **Context Compaction:** Write state to `MEMORY.md` instead of relying on chat history during long sessions — update it after every milestone.
4. **Iterative Verification:** Run tests/linters after each logical change. Fix errors before moving on (see `REVIEW-CHECKLIST.md`).
5. **Browser Verification:** For any UI change (especially the swipe deck), actually run the app and test it on a mobile viewport before calling it done.

## How I Should Think
1. **Understand Intent First:** Identify what the user actually needs before answering.
2. **Ask If Unsure:** If critical information is missing (e.g., which hosting target for FastAPI), ask before proceeding.
3. **Plan Before Coding:** Propose a plan, get approval, then implement.
4. **Verify After Changes:** Run tests/linters or do a manual check after each change.
5. **Explain Trade-offs:** When recommending an approach, briefly mention the alternative and why you didn't pick it.

## Context Files
Load only when needed — don't dump all of these into context at once:
- `agent_docs/tech_stack.md` — exact libraries, versions, setup commands, code examples
- `agent_docs/code_patterns.md` — architecture boundaries, data fetching, error handling, naming
- `agent_docs/project_brief.md` — product vision, conventions, quality gates
- `agent_docs/product_requirements.md` — full feature list, user story, success metrics
- `agent_docs/testing.md` — test strategy and verification loop

## Current State
**Last Updated:** 2026-06-09
**Working On:** All three Phase 2 "Must Have" features complete — ready for Phase 3 polish (error handling, mobile responsiveness pass, performance) or Phase 4 deployment
**Recently Completed:**
- Vision Ingestion Pipeline (Feature 1), verified end-to-end in the browser on a real photo:
  - `backend/app/services/background_removal.py` — `briaai/RMBG-1.4` via `transformers` (pinned to `4.49.0`; see Known Issues), strips backgrounds in ~2s
  - `backend/app/services/vlm_tagging.py` — Gemini 2.5 Flash via direct REST calls (httpx + `responseSchema` structured output), validated by the extended `ItemTags` Pydantic model (added a `category` field — see Known Issues)
  - `backend/app/services/embeddings.py` — `sentence-transformers/all-MiniLM-L6-v2` embeds a natural-language rendering of the tags, upserted into the `lime-items` Pinecone index
  - `backend/app/routers/items.py` — `POST /items/ingest` orchestrates all three stages statelessly, mints the item's UUID, returns `{item_id, tags, stripped_image_base64}`
  - `frontend/src/app/ingest/` — the "Ingestion Camera": upload form (`ingest-form.tsx`, live preview + loading state) and a Server Action (`actions.ts`) that calls FastAPI, then writes the stripped image to Supabase Storage and inserts the `items` row using the user's authenticated session
  - Linked from `/wardrobe` via an "Add an item" button
- Lime-accent design system (via the `ui-ux-pro-max` plugin's design-intelligence search) — Outfit/Work Sans typography, lime oklch theme tokens layered onto Shadcn's "Nova" base — see `MEMORY.md` for the full rationale and palette values
- Tinder-Style Swiping UI (Feature 3 — the "Styling Deck"), verified end-to-end in the browser at a 375×812 mobile viewport:
  - `frontend/src/app/deck/actions.ts` — `getWardrobe()`/`lockOutfit()` Server Actions (signed Supabase Storage URLs; `images.remotePatterns` added to `next.config.ts`)
  - `frontend/src/app/deck/components/{swipe-card,style-stack,deck-board}.tsx` — framer-motion drag gestures with spring physics, single-stack-at-a-time tabbed layout (a thumbnail switcher doubles as a live outfit preview)
  - Linked from `/wardrobe` via a "Style a fit" button
  - Found and fixed a real mobile-layout bug mid-verification (the fixed "Lock this fit" CTA bar overlapped and intercepted swipe gestures on the Bottom/Shoes stacks when all three were stacked vertically) — see `MEMORY.md` for the diagnosis and the tabbed-layout redesign that fixed it
- Weather-query half of the Recommendation Engine (Feature 2's remaining piece), verified end-to-end in the browser with Playwright's geolocation mocking:
  - `backend/app/services/weather.py` — keyless Open-Meteo forecast lookup (current temperature + WMO weather code → plain-English condition)
  - `backend/app/services/recommendations.py` — temperature → natural-language "ideal outfit" sentence → embed (reusing the same MiniLM model/index from `embeddings.py`) → Pinecone query ranked per category, filtered to the user's own wardrobe
  - `backend/app/routers/recommendations.py` — `GET /recommendations?user_id=&latitude=&longitude=`
  - `frontend/src/app/deck/components/weather-widget.tsx` + `DeckBoard` wiring — browser Geolocation API → `getRecommendations` Server Action → reorders each stack so the weather-matched item surfaces first (`reorderByRanking`), with a live "−33°C and clear — picks dressed for it" readout above the stacks (per the PRD's "real-time weather widget" spec). Declining/lacking location just keeps the default ordering — never blocks the deck.
  - **Fixed a real prerequisite gap**: Pinecone vectors had no `user_id` in metadata, so a similarity query couldn't be scoped per-user — added `user_id`+`category` to the upsert metadata and threaded `user_id` through as a new required field on `POST /items/ingest` (additive, backward-compatible; old vectors simply won't match filtered queries — see `MEMORY.md` Known Issues for the 2 harmless orphans left in the index).
**Blocked By:** Nothing — Phase 2 is complete; ready for Phase 3 polish whenever you want to start it

## Roadmap

### Phase 1: Foundation — ✅ COMPLETE
- [x] Scaffold Next.js (App Router) frontend with Tailwind + Shadcn/ui — `frontend/`, Next.js 16.2.7, lint + build pass
- [x] Scaffold FastAPI backend service (project skeleton, `/health` endpoint) — `backend/`, verified `GET /health` → `{"status": "ok"}`
- [x] Create Supabase project, Pinecone Starter index (`lime-items`, 384-dim, cosine, serverless), and Gemini API key — all verified reachable via `backend/scripts/smoke_test.py`
- [x] Define Postgres schema (`profiles`, `items`, `outfits`) in Supabase, enable Auth, create a `clothing-photos` Storage bucket with RLS policies scoped to the owning user — see `supabase/schema.sql`, verified live in the database
- [x] Wire Supabase Auth into the Next.js app via `@supabase/ssr` (deviation from Tech Design's `@supabase/auth-helpers-nextjs`, which is deprecated) — verified live in a headless browser

### Phase 2: Core Features (from PRD "Must Have")
- [x] **Feature 1 — One-Click Vision Ingestion Pipeline:** upload → `briaai/RMBG-1.4` background removal → Gemini 2.5 Flash structured JSON tagging (silhouette, palette, texture, aesthetic, **+ category**), validated with Pydantic, embedded, upserted to Pinecone, persisted to Supabase. Verified end-to-end in the browser on a real photo: ~13s from upload to "Saved to your wardrobe ✓", with Postgres/Storage/Pinecone all confirmed holding the joined `item_id`.
- [x] **Feature 2 — Vector-Driven Recommendation Engine:** embedding/upsert half (Feature 1) + weather-query half: `GET /recommendations` calls Open-Meteo for local temperature/condition, embeds an "ideal outfit" sentence, queries Pinecone filtered to the user's wardrobe and ranked per category. Verified end-to-end with Playwright geolocation mocking (Antarctica coords → "−33°C and clear" widget, cold-weather items correctly ranked first in all three stacks).
- [x] **Feature 3 — Tinder-Style Categorized Swiping UI:** independent swipeable stacks for Tops/Bottoms/Shoes using `framer-motion`, smooth on mobile (single-stack-at-a-time tabbed layout with a live outfit-preview switcher), lets users lock one layer while cycling others. Verified end-to-end at a 375×812 mobile viewport: swipe-to-cycle works on all three categories, "Lock this fit" writes the correct `top/bottom/shoes_item_id` combo to `outfits`. Live at `/deck`, linked from `/wardrobe`.

### Phase 3: Polish
- [ ] Error handling for malformed VLM JSON output (must never crash the pipeline — PRD explicitly calls this out)
- [ ] Mobile responsiveness and swipe-gesture performance pass (no lag — PRD explicitly calls this out)
- [ ] The Wardrobe Grid screen (categorized, background-stripped thumbnails)

### Phase 4: Launch
- [ ] Deploy Next.js to Vercel (Hobby tier)
- [ ] Deploy FastAPI service (Render or Hugging Face Spaces — confirm $0 option)
- [ ] Configure test-group accounts and roll out to early testers
- [ ] Validate against Success Metrics (see `agent_docs/product_requirements.md`)

## What NOT To Do
- Do NOT delete files without explicit confirmation
- Do NOT modify Supabase migrations or RLS policies without a backup plan
- Do NOT add anything from the "Future Features" table (Pinterest syncing, resale agent) — that's V1.5/V2.0
- Do NOT skip tests for "simple" changes, especially around the JSON tagging contract
- Do NOT introduce a paid tier or paid dependency — the budget constraint is $0/month, full stop
- Do NOT bypass failing tests or pre-commit hooks
