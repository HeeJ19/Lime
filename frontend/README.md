# Lime — Frontend

Next.js (App Router) frontend for Lime. Handles auth, the wardrobe UI, and orchestration between Supabase and the FastAPI AI service. See the [root README](../README.md) for the full project overview and [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) for how this fits into the rest of the system.

## Stack

Next.js 16 (App Router) · React 19 · TypeScript · Tailwind CSS v4 · shadcn/ui · framer-motion · Supabase (`@supabase/ssr`)

## Getting started

```bash
npm install
cp .env.local.example .env.local   # fill in Supabase project URL/anon key + backend URL
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). You'll need:

- A Supabase project with the schema in [`../supabase/schema.sql`](../supabase/schema.sql) applied
- The FastAPI backend running locally (default `http://127.0.0.1:8001`) or pointed at the deployed Space

## Scripts

| Command | Purpose |
| :-- | :-- |
| `npm run dev` | Start the dev server |
| `npm run build` | Production build |
| `npm run start` | Run the production build |
| `npm run lint` | Lint with ESLint |

## Structure

```
src/
├── app/
│   ├── auth/          # Login/signup server actions + callback route
│   ├── login/, signup/
│   ├── ingest/        # Photo upload → AI tagging flow
│   ├── wardrobe/      # Grid view of all items
│   └── deck/          # Weather-aware swipe deck
├── components/ui/     # shadcn/ui primitives
├── lib/supabase/      # Browser/server Supabase clients
└── middleware.ts      # Session refresh (Supabase SSR)
```
