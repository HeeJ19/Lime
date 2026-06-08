# Product Requirements

> Source: `docs/PRD-[Lime]-MVP.md`. This is the authoritative feature/scope list — when in doubt about whether something belongs in the MVP, check here.

## Overview
**Product Name:** Lime
**Problem Statement:** Existing digital wardrobe apps either require exhausting manual data entry or rely on rigid, rule-based logic that suggests clashing outfits. Lime automates closet curation using computer vision and delivers aesthetic, weather-optimized outfit combinations through vector embeddings.
**MVP Goal:** Deploy a functional full-stack web prototype operating entirely on free tiers to a core group of early testers to validate automated tagging and vector-based matchmaking.
**Target Launch:** Rapid 4-week development cycle.

## Primary User Story
> Alex snaps a quick photo of a jacket on his bed. Within seconds, the background is stripped, and Lime classifies it perfectly down to its palette and aesthetic type. The next morning, Alex opens Lime. The app detects the local chilly weather and presents a swipeable stack of coordinated outfits. He likes the jacket but wants different shoes, so he swipes through his shoe collection stack until a perfect color-theory match clicks. He goes out the door in minutes.

**Key touchpoints:** Discovery (frictionless organization) → Onboarding (zero manual fields, just an image) → Core Loop (Snap → Auto-Tag → Store in Vector DB) → Retention (daily weather-based swiping recommendations).

## Must-Have Features (MVP)

### 1. One-Click Vision Ingestion Pipeline
- **Description:** User uploads a raw photo; backend strips the background (open-source model) and runs VLM tagging.
- **User Value:** Eliminates the grueling manual entry required by existing closet apps.
- **Success Criteria:**
  - Background stripped successfully using `briaai/RMBG-1.4`.
  - Gemini 2.5 Flash outputs structured JSON tags (silhouette, palette, texture, aesthetic) within 3 seconds.

### 2. Vector-Driven Recommendation Engine
- **Description:** Converts JSON metadata into high-dimensional vector embeddings stored in a vector database.
- **User Value:** Guarantees fluid, nuanced aesthetic matching over clashing rule-based logic.
- **Success Criteria:** Pulls real-time local temperatures via Open-Meteo API and queries Pinecone to return matching style clusters.

### 3. Tinder-Style Categorized Swiping UI
- **Description:** Mobile-responsive layout with independent swipeable card stacks for Tops, Bottoms, and Shoes.
- **User Value:** Reduces decision fatigue by letting users lock one piece of an outfit while cycling through others dynamically.
- **Success Criteria:** Smooth touch-and-swipe gesture performance on mobile viewports; users can independently change layers of a single outfit recommendation.

## Explicitly NOT in MVP
| Feature | Why Wait | Planned For |
| :--- | :--- | :--- |
| Pinterest Style Syncing | Requires crawling external visual boards; focus first on local wardrobe. | Version 1.5 |
| Closed-Loop Resale Agent | MCP web scraping on market valuations takes extra time to refine. | Version 2.0 |

## Success Metrics
- **Short term (1 month):** 100% of core testers successfully upload at least 5 items without backend pipeline failures.
- **Medium term (3 months):** At least 3 outfit configurations built and locked per user weekly via the swiping interface.

## UI/UX Direction
**Design Feel:** Clean, fast, minimal, high-end streetwear boutique aesthetic.

**Key Screens:**
1. **The Ingestion Camera:** Simple camera wrapper/upload component with immediate loading feedback.
2. **The Styling Deck:** Core interface — 3 vertically stacked Tinder-style swipe cards (Tops, Bottoms, Shoes) below a real-time weather widget.
3. **The Wardrobe Grid:** Clean visual matrix of categorized clothes with high-resolution, background-stripped thumbnails.

## Constraints
- **Budget:** Strict $0/month — Vercel Hobby, Pinecone Starter, Gemini 2.5 Flash free tier.
- **Timeline:** 3-4 weeks to a functional local test-group prototype.

## Quality Standards (What Lime Will NOT Accept)
- Raw hex code or rigid text-tag matches for styling — must leverage embeddings.
- Sluggish card swiping animation lag on mobile web.
- Broken JSON parsing when the VLM outputs metadata.

## MVP Completion Checklist
**Development Complete**
- [ ] FastAPI backend handles background removal and Gemini VLM parsing securely.
- [ ] Pinecone successfully indexes and queries item embeddings.
- [ ] Next.js frontend delivers responsive independent Tinder card swiping mechanics.

**Launch Ready**
- [ ] Next.js deployed seamlessly to Vercel.
- [ ] Test group accounts configured for rollout.
