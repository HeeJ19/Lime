# Code Patterns

## Purpose
Implementation patterns the agent should follow for Lime. Prefer these over inventing new ones.

## Architecture Pattern
- **Primary pattern:** Monolithic frontend (Next.js) + decoupled AI microservice (FastAPI) — exactly as specified in the Tech Design. This is a hard boundary, not a suggestion.
- **Rule:** Next.js handles UI, routing, auth, and orchestration (calling the FastAPI service, querying Supabase/Pinecone for display). It does NOT run ML models or call Gemini directly.
- **Rule:** FastAPI owns the entire AI pipeline: background removal, VLM tagging, JSON validation, embedding generation, Pinecone upserts. Keep this service stateless and focused.
- **Rule:** Reuse existing modules before creating new abstractions — this is a 4-week MVP, not a platform.

## Data Fetching
- **Frontend → Backend:** Next.js Server Actions handle file upload and call the FastAPI endpoint.
- **Frontend → Supabase:** Use the Supabase JS client (via `@supabase/auth-helpers-nextjs`) for auth-protected queries against Postgres/Storage.
- **Frontend → Recommendations:** query flow is Open-Meteo (get local temperature) → FastAPI/Pinecone (filter by aesthetic cluster) → render swipe stacks.
- **Rule:** Keep fetch logic in Server Actions / route handlers, not inside render functions.

## State Management
- **Server state:** Supabase Postgres is the source of truth for item metadata and user data; Pinecone is the source of truth for embeddings/similarity.
- **Client state:** Local component state (React `useState`/`useReducer`) is sufficient for the swipe deck's "current card index per stack" — do not add a state management library for an MVP this size.
- **Forms:** Keep the ingestion form minimal (image upload only — the PRD's whole point is "zero manual input fields").

## Error Handling
- Validate every Gemini JSON response with Pydantic at the FastAPI boundary — never let a raw/malformed VLM response reach Pinecone, Postgres, or the UI.
- Normalize errors at the FastAPI/Next.js boundary into a consistent shape (e.g., `{ error: { code, message } }`).
- Never swallow pipeline errors silently — log them server-side and surface a user-safe message ("Couldn't read that item, try a clearer photo") in the UI.

## Validation
- **External inputs:** uploaded images (size/type checks before sending to the backend), Gemini's JSON tag output (Pydantic models — see `tech_stack.md`).
- **Boundary rule:** validate at the FastAPI entrypoints; trust validated data once it's inside the pipeline.
- Co-locate Pydantic schemas with the endpoints that use them.

## File and Naming Conventions
- **Frontend files:** kebab-case for files/routes (Next.js App Router default), PascalCase for components, camelCase for functions/variables
- **Backend files:** snake_case (Python convention)
- **Components / classes:** PascalCase
- **Constants / env vars:** UPPER_SNAKE_CASE (`GEMINI_API_KEY`, `PINECONE_INDEX_NAME`, etc.)

## Testing Pattern
- Unit tests for pure logic: tag-to-embedding conversion, weather-to-query-filter mapping, Pydantic schema validation
- Integration tests for the two critical flows: (1) upload → background removal → tagging → embedding → Pinecone upsert, and (2) weather lookup → Pinecone query → recommendation stack
- E2E tests (if time allows in the 4-week sprint) for the swipe interaction on a mobile viewport
- Run the relevant test suite after every feature; fix failures before moving on — see `testing.md`

## Change Discipline
- Prefer focused, minimal edits over large rewrites — this is an MVP on a hard deadline.
- Do not introduce new dependencies without checking `tech_stack.md` first, and confirming it fits the $0/month budget.
- Do not touch Supabase migrations, RLS policies, Pinecone index config, or deployment config without explicit approval (see Protected Areas in `AGENTS.md`).
- One feature at a time — checkpoint/commit after each working feature, then move to the next item in the Phase 2 roadmap.
