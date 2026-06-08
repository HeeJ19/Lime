# Tech Stack & Tools

## Frontend
- **Framework:** Next.js (App Router) — hosted on Vercel (Hobby tier, $0)
- **Styling:** Tailwind CSS + Shadcn/ui — chosen for fast, high-end "streetwear boutique" components matching the PRD's design direction
- **Animation/Gestures:** `framer-motion` — powers the Tinder-style swipe cards
- **Auth:** `@supabase/auth-helpers-nextjs` for server-side auth protection
- **Performance:** Use Next.js `dynamic` imports for the heavy swiping components so initial page loads stay fast

## Backend (AI Microservice)
- **Framework:** Python (FastAPI) — deploy to a free host (Render or Hugging Face Spaces; confirm which before Phase 1 is done)
- **Background Removal:** `briaai/RMBG-1.4` — small (44.1M param) open-source segmentation model, run locally via the `transformers` pipeline
- **VLM Tagging:** Gemini 2.5 Flash API (free tier) — given a background-stripped image + a strict system prompt, returns structured JSON: `silhouette`, `palette`, `texture`, `aesthetic`
- **Validation:** Pydantic models validate every Gemini JSON response before it reaches the database — this is non-negotiable per the PRD ("Broken JSON parsing" is an explicit quality failure)

## Database, Auth & Storage
- **Supabase** (free tier): PostgreSQL for metadata, Supabase Auth for users, Supabase Storage for clothing photos
- **Security:** Row Level Security (RLS) must be enabled on Storage buckets and tables holding user clothing photos (data sensitivity requirement from the Tech Design)

## Vector Search
- **Pinecone** (Starter tier, $0, up to 100K vectors): stores high-dimensional embeddings generated from the JSON tags, queried for outfit recommendations

## External APIs
- **Open-Meteo** (no API key, 10K free calls/day): provides local weather/temperature used to filter Pinecone queries by aesthetic clusters suitable for current conditions

## Setup Commands
*(Confirm exact commands once the project is scaffolded and update this section)*
```bash
# Frontend (run inside the Next.js app directory)
npm install
npm run dev

# Backend (run inside the FastAPI service directory)
pip install -r requirements.txt
uvicorn main:app --reload
```

## Pipeline Reference (from Tech Design)
1. Next.js Server Action uploads the image blob → POST to FastAPI
2. FastAPI runs `briaai/RMBG-1.4` locally to strip the background
3. Stripped image sent to Gemini 2.5 Flash → structured JSON tags returned
4. Pydantic validates the JSON → tags converted to vector embeddings → upserted into Pinecone
5. Metadata returned to the frontend; on the recommendation side, Open-Meteo temperature filters the Pinecone query to surface matching outfit clusters

## Error Handling Pattern (FastAPI + Pydantic)
```python
# Validate the VLM's JSON output before it ever reaches Pinecone or Postgres.
# If Gemini returns malformed JSON, fail loudly here — never let bad data propagate.
from pydantic import BaseModel, ValidationError

class ItemTags(BaseModel):
    silhouette: str
    palette: list[str]
    texture: str
    aesthetic: str

def parse_vlm_response(raw_json: str) -> ItemTags:
    try:
        return ItemTags.model_validate_json(raw_json)
    except ValidationError as e:
        # Log the raw response for debugging, then surface a clean error
        # to the frontend instead of a raw 500.
        raise ValueError(f"VLM returned invalid tag JSON: {e}") from e
```

## Styling & Component Example (Next.js + Tailwind + Shadcn/ui)
```tsx
// Example: a single swipeable item card using shadcn/ui primitives + framer-motion.
// Keep ML/data logic out of this component — it should only render what it's given.
import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";

export function StyleCard({ imageUrl, label }: { imageUrl: string; label: string }) {
  return (
    <motion.div drag="x" dragConstraints={{ left: 0, right: 0 }} whileTap={{ scale: 0.97 }}>
      <Card className="overflow-hidden rounded-2xl shadow-md">
        <CardContent className="p-0">
          <img src={imageUrl} alt={label} className="aspect-[3/4] w-full object-cover" />
        </CardContent>
      </Card>
    </motion.div>
  );
}
```
