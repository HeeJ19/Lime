# Project Brief

- **Product vision:** Lime automates closet curation with computer vision and recommends weather-aware, aesthetically-coherent outfits via vector embeddings — replacing the manual entry and rigid rule-based matching that make existing wardrobe apps (Indyx, Acloset, Whering) frustrating.
- **Target Audience:** Fashion-conscious individuals and everyday users who experience morning decision fatigue, want to get more wear out of their wardrobe, and don't have time to manually catalog items.
- **Design feel:** Clean, fast, minimal, high-end streetwear boutique aesthetic (drives the Tailwind + Shadcn/ui choice).

## Conventions
- **Naming:** kebab-case for Next.js files/routes, PascalCase for components, camelCase for functions/variables (frontend); snake_case for Python modules (backend). See `code_patterns.md` for the full list.
- **File Structure:** Keep the Next.js app and the FastAPI service as clearly separated directories/projects — they deploy independently (Vercel vs. Render/HF Spaces).
- **Architecture boundary:** UI/orchestration in Next.js, all ML/AI work in FastAPI. Do not blur this line (see `code_patterns.md`).

## Quality Gates
- Pydantic validation on every Gemini JSON response — broken JSON parsing is an explicit PRD failure condition.
- Smooth, lag-free swipe gestures on mobile viewports — explicit PRD failure condition if sluggish.
- Background removal must succeed via `briaai/RMBG-1.4` and tagging must complete within 3 seconds (PRD success criteria for Feature 1).
- RLS enabled on all Supabase Storage/tables holding user clothing photos.

## Key Commands
*(Fill in once the project is scaffolded — see `tech_stack.md` for the current placeholders)*
- Frontend dev: `npm run dev`
- Frontend test: `npm test`
- Backend dev: `uvicorn main:app --reload`
- Backend test: `pytest`

## Key Principles
- Ship the simplest possible solution that satisfies the user story in `product_requirements.md`.
- Prefer managed/free-tier services over custom builds — Supabase and Pinecone exist precisely so you don't have to write your own auth, storage, or vector index.
- Stay inside the $0/month budget. If a suggested approach requires a paid tier or paid dependency, stop and flag it instead of proceeding.
- Anything in the PRD's "Future Features" table (Pinterest syncing, resale agent) is explicitly out of scope for this build — don't get pulled into it.

## Update Cadence
Refresh this brief whenever a Phase completes, an architectural decision changes, or a new constraint emerges. Log the actual decision in `MEMORY.md` first, then reflect any persistent rule change here.
