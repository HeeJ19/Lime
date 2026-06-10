# Product Requirements Document: Lime MVP

## Overview

**Product Name:** Lime
**Problem Statement:** Existing digital wardrobe apps either require exhausting manual data entry or rely on rigid, rule-based logic that suggests clashing outfits. Lime automates closet curation using computer vision and delivers aesthetic, weather-optimized outfit combinations through vector embeddings.
**MVP Goal:** Deploy a functional full-stack web prototype operating entirely on free tiers to a core group of early testers to validate automated tagging and vector-based matchmaking.
**Target Launch:** As soon as possible (Rapid 4-week development cycle).

## Target Users

### Primary User Profile
* **Who:** Fashion-conscious individuals and everyday users facing morning decision fatigue.
* **Problem:** They want to maximize their wardrobe utility and look good, but they lack the time to manually catalog items or plan outfits every morning.
* **Current Solutions:** Apps like Indyx (too manual) or Acloset/Whering (rigid, clashing suggestions).
* **Why They'll Switch:** Lime provides a zero-effort setup via instant vision tagging and fluid, embedding-based style matching.

---

## User Journey

### The Story
Alex snaps a quick photo of a jacket on his bed. Within seconds, the background is stripped, and Lime classifies it perfectly down to its palette and aesthetic type. The next morning, Alex opens Lime. The app detects the local chilly weather and presents a swipeable stack of coordinated outfits. He likes the jacket but wants different shoes, so he swipes through his shoe collection stack until a perfect color-theory match clicks. He goes out the door in minutes.

### Key Touchpoints
1. **Discovery:** User wants a frictionless way to organize their style.
2. **Onboarding:** Zero manual input fields. User takes or uploads an image.
3. **Core Loop:** Snap → Auto-Tag → Store in Vector Database.
4. **Retention:** Daily weather-based swiping recommendation stacks.

---

## MVP Features

### Core Features (Must Have)

#### 1. One-Click Vision Ingestion Pipeline
* **Description:** User uploads a raw photo of an item. The backend strips the background using an open-source model and runs VLM tagging.
* **User Value:** Eliminates the grueling manual entry required by existing closet apps.
* **Success Criteria:** 
  * Background stripped successfully using `briaai/RMBG-1.4`.
  * Gemini 2.5 Flash outputs structured JSON tags (silhouette, palette, texture, aesthetic) within 3 seconds.

#### 2. Vector-Driven Recommendation Engine
* **Description:** Converts JSON metadata into high-dimensional vector embeddings stored in a vector database.
* **User Value:** Guarantees fluid, nuanced aesthetic matching over clashing rule-based logic.
* **Success Criteria:** Pulls real-time local temperatures via Open-Meteo API and queries Pinecone to return matching style clusters.

#### 3. Tinder-Style Categorized Swiping UI
* **Description:** A mobile-responsive layout presenting independent swipeable card stacks for Tops, Bottoms, and Shoes. 
* **User Value:** Reduces decision fatigue by letting users lock one piece of an outfit while cycling through others dynamically.
* **Success Criteria:** Smooth touch-and-swipe gesture performance on mobile viewports, allowing users to independently change layers of a single outfit recommendation.

### Future Features (Not in MVP)
| Feature | Why Wait | Planned For |
| :--- | :--- | :--- |
| Pinterest Style Syncing | Requires crawling external visual boards; focus first on local wardrobe. | Version 1.5 |
| Closed-Loop Resale Agent | MCP web scraping on market valuations takes extra time to refine. | Version 2.0 |

---

## Success Metrics

### Primary Metrics
* **Short term (1 month):** 100% of core testers successfully upload at least 5 items without backend pipeline failures.
* **Medium term (3 months):** At least 3 outfit configurations built and locked per user weekly via the swiping interface.

---

## UI/UX Direction

**Design Feel:** Clean, fast, minimal, high-end streetwear boutique aesthetic.

### Key Screens
1. **The Ingestion Camera:** Simple camera wrapper/upload component with immediate loading feedback.
2. **The Styling Deck:** The core interface featuring 3 separate vertically stacked Tinder-style swipe cards (Tops, Bottoms, Shoes) sitting below a real-time weather widget.
3. **The Wardrobe Grid:** A clean visual matrix displaying categorized clothes with high-resolution, background-stripped asset thumbnails.

---

## Constraints & Requirements

### Budget (Strict $0/Month Constraint)
* **Frontend/Hosting:** Vercel Hobby Tier ($0).
* **Database & Vector Search:** Pinecone Starter Tier ($0).
* **AI Compute:** Gemini 2.5 Flash Free Tier API ($0).

### Timeline
* **MVP Build Sprint:** 3-4 weeks to a functional local test-group prototype.

---

## Quality Standards

**What Lime Will NOT Accept:**
* Raw hex code or rigid text-tag matches for styling (must leverage embeddings).
* Sluggish card swiping animation lag on mobile web.
* Broken JSON parsing when the VLM outputs metadata.

---

## MVP Completion Checklist

### Development Complete
* [ ] FastAPI backend handles background removal and Gemini VLM parsing securely.
* [ ] Pinecone successfully indexes and queries item embeddings.
* [ ] Next.js frontend delivers responsive independent Tinder card swiping mechanics.

### Launch Ready
* [ ] Next.js deployed seamlessly to Vercel.
* [ ] Test group accounts configured for rollout.
