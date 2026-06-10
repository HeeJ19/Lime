---
title: Lime AI Backend
emoji: 🍋
colorFrom: green
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
---

# Lime AI Backend

FastAPI microservice for the Lime digital wardrobe app.

**Endpoints:**
- `GET /health` — liveness check
- `POST /items/ingest` — background removal (RMBG-1.4) + VLM tagging (Gemini 2.0 Flash) + Pinecone embedding
- `GET /recommendations` — Open-Meteo weather → Pinecone similarity search → ranked item IDs

**Required Space secrets** (Settings → Variables and secrets):
- `GEMINI_API_KEY`
- `PINECONE_API_KEY`
- `PINECONE_INDEX_NAME`

**Testing:**
```bash
pip install -r requirements-dev.txt
pytest
```
The suite mocks Gemini, Open-Meteo, and Pinecone, so it runs without any of the secrets above — covering tag validation, the ingestion/recommendation routes, and weather/aesthetic ranking logic.
