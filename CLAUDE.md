# CLAUDE.md — Claude Code Configuration for Lime

## Project Context
**App:** Lime — AI-powered digital wardrobe app (auto-tagging via computer vision + weather-aware outfit recommendations via vector embeddings)
**Stack:** Next.js (App Router, Tailwind, Shadcn/ui, framer-motion) + Python FastAPI AI microservice (briaai/RMBG-1.4, Gemini 2.5 Flash) + Supabase (Postgres/Auth/Storage) + Pinecone + Open-Meteo
**Stage:** MVP Development (4-week sprint, strict $0/month budget)
**User Level:** In-between — learning while building. Explain *why* behind architectural choices, not just *what* to type; flag concepts that are non-obvious (e.g., why ML logic stays out of Next.js).

## Directives
1. **Master Plan:** Always read `AGENTS.md` first — it has the current phase, roadmap, and protected areas.
2. **Documentation:** Pull from `agent_docs/` only as needed: `tech_stack.md` for exact libraries/setup, `code_patterns.md` for architecture/style rules, `product_requirements.md` for the full feature spec, `testing.md` for verification steps, `project_brief.md` for persistent conventions.
3. **Plan-First:** Propose a brief plan and wait for approval before touching more than one file. Use Plan Mode for anything that spans the frontend/backend boundary.
4. **Incremental Build:** Build one feature from the Phase 2 roadmap at a time. Test it, verify it in the browser if it's UI, then move on.
5. **Memory:** Update `MEMORY.md` after each milestone or architectural decision — don't let context fill up with state that belongs in a file.
6. **Pre-Commit:** If hooks exist, run them before commits and fix failures — don't bypass with `--no-verify`.
7. **No Linting Duty:** Don't act as a human linter. Run `npm run lint` / `ruff check .` and fix what they report.
8. **Communication:** Be concise. Ask one specific clarifying question when something's ambiguous (e.g., which free host for FastAPI) rather than guessing.
9. **Continuity:** If starting a fresh session mid-build, read `AGENTS.md` → `MEMORY.md` → relevant `agent_docs/` file before writing any code, so you don't restart from a blank slate.

## Commands
*(Confirm and update once the project is scaffolded — see `agent_docs/tech_stack.md`)*
- `npm run dev` — Start the Next.js frontend
- `npm test` — Run frontend tests
- `npm run lint` — Check frontend code style
- `uvicorn main:app --reload` — Start the FastAPI backend
- `pytest` — Run backend tests
