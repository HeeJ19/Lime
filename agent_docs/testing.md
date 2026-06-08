# Testing Strategy

## Frameworks
- **Frontend Unit/Component Tests:** Vitest (or Jest, whichever `create-next-app` scaffolds by default)
- **Backend Unit/Integration Tests:** `pytest`
- **E2E Tests:** Playwright — prioritize the swipe-deck flow on a mobile viewport, since that's the PRD's most demanding UX requirement
- **Manual Checks:** browser-based mobile-viewport testing of the swipe deck; manual upload tests with real clothing photos to sanity-check the tagging pipeline end to end

## What to Test (mapped to PRD success criteria & quality standards)
- **Vision Ingestion Pipeline:** background removal succeeds, Gemini returns valid JSON within 3 seconds, Pydantic validation rejects malformed responses cleanly (never crashes the pipeline)
- **Recommendation Engine:** Open-Meteo lookup returns a temperature, Pinecone query returns relevant style clusters for that temperature, embeddings are generated correctly from tags
- **Swiping UI:** independent stacks for Tops/Bottoms/Shoes behave correctly, swipe gestures are smooth with no lag on mobile viewports, locking one layer while cycling others works as described in the user story

## Rules & Requirements
- **Coverage focus:** prioritize the two pipeline-critical paths (ingestion → tagging → embedding → storage, and weather → recommendation query) over chasing a coverage percentage — this is a 4-week MVP.
- **Before marking a feature complete:** run the relevant test suite (`pytest` for backend changes, `npm test` for frontend changes) and do a manual browser check for any UI change.
- **Failures:** NEVER skip tests or mock out assertions to force a pipeline to pass without explicit human approval. If you break a test, fix it before moving on.
- **JSON contract tests are non-negotiable:** every change touching the Gemini tagging flow must include a test that feeds it a malformed/unexpected response and confirms Pydantic catches it gracefully — this directly maps to the PRD's "Broken JSON parsing" failure condition.

## Execution
*(Confirm exact commands once the project is scaffolded and update this section)*
- Run all backend tests: `pytest`
- Run a single backend test file: `pytest path/to/test_file.py`
- Run all frontend tests: `npm test`
- Run a single frontend test file: `npm test -- path/to/file.test.tsx`

## Verification Loop
1. Implement one feature from the Phase 2 roadmap in `AGENTS.md`.
2. Run the relevant automated tests; fix failures before continuing.
3. For UI changes, start the dev server and manually verify in a browser at a mobile viewport width.
4. Update `MEMORY.md` with any new architectural decisions or known issues discovered along the way.
5. Move to the next roadmap item only after the above checks pass — see `REVIEW-CHECKLIST.md` before declaring a feature done.
