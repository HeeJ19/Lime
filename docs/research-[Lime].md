# Deep Research Report: Loom (Autonomous Digital Wardrobe)

### 1. Market Validation & Competitor Teardown

Loom is positioned to disrupt current styling apps by replacing rigid logic and manual labor with dynamic, embedded intelligence. Here is how Loom compares to the current market landscape:

| Competitor | Core Approach | Critical Flaws to Exploit | Loom's Differentiation |
| :--- | :--- | :--- | :--- |
| **Indyx** | Analytics and cost-per-wear tracking. | Requires tedious manual entry or relying on expensive human archivists. | Automated metadata extraction via VLM completely removes manual entry friction. |
| **Whering / Acloset** | Gen-Z utility and outfit tracking. | Relies heavily on rigid, semantic "if/then" styling logic that leads to mismatched aesthetics. | High-dimensional vector embeddings match aesthetic nuances based on weather and color theory. |
| **Nouva / Selion.ai** | AI-driven styling and curation. | Function purely as closed visual ecosystems, limiting user utility. | An open MCP web scraping agent that directly connects items to secondary markets (eBay/Grailed). |

### 2. Recommended Tech Stack ($0/Month Architecture)

To keep costs strictly at $0, we will heavily leverage generous free tiers and open-source models. 

| Layer | Recommended Tool | Free Tier Limitations | Source URL (Accessed June 8, 2026) |
| :--- | :--- | :--- | :--- |
| **Frontend** | **Next.js (Vercel)** | Hobby tier allows 100 CLI deployments per day and 1 million function invocations. | `vercel.com/docs/limits` |
| **Backend** | **Python (FastAPI)** | Free hosting options like Render or Hugging Face Spaces. | N/A |
| **Vector DB** | **Pinecone** | The Starter plan covers up to 100,000 vectors for $0/month. | `docs.pinecone.io/guides/manage-cost/understanding-cost` |
| **Vision LLM** | **Gemini 2.5 Flash** | 10 requests per minute (RPM) and 250,000 tokens per minute (TPM). | `aifreeapi.com/en/posts/gemini-api-rate-limits-per-tier` |
| **Weather API** | **Open-Meteo** | Allows 10,000 free API calls per day without requiring an API key. | `open-meteo.com/en/pricing` |
| **BG Removal** | **briaai/RMBG-1.4** | Free, source-available model for non-commercial use that can be run locally. | `huggingface.co/briaai/RMBG-1.4` |

> **Note on Conflicting Information:** Free-tier limits vary significantly among providers. For example, while Google's Gemini 2.5 Flash API explicitly limits free users to 10 RPM, Groq's Llama 4 Maverick offers up to 30 RPM and 1,000 requests per day. If Gemini's 10 RPM rate limit throttles your image upload speed, you can swap to Groq's API for faster sequential tagging.

### 3. AI Tool Guide & Pipeline Strategy

**Task 1: Background Removal**
*   **Tool:** `briaai/RMBG-1.4` (Hugging Face)
*   **Why:** It is a state-of-the-art segmentation model trained on high-quality licensed images. Because it is a small 44.1M parameter model, you can easily run it directly in your Python FastAPI backend using the `transformers` pipeline to strip backgrounds instantly before sending data to the VLM.

**Task 2: Vision Metadata Tagging (JSON)**
*   **Tool:** Gemini 2.5 Flash API
*   **Why:** It is lightweight, fast, and highly capable of multimodal reasoning. You can pass the background-stripped image and a strict system prompt (e.g., "Output ONLY valid JSON containing: Silhouette, Color Palette, Texture, Aesthetic") directly to the Gemini API. 

**Task 3: Outfit Recommendations**
*   **Tool:** Pinecone Vector Search + Open-Meteo
*   **Why:** When Gemini outputs the JSON tags, use a lightweight Python embedding model to convert those tags into vectors and store them in Pinecone. When a user requests an outfit, hit the Open-Meteo API (which provides high-resolution local weather models). Use the temperature variables to filter your vector search in Pinecone to find the closest matching aesthetic clusters suitable for that weather.

**Task 4: Secondary Market Scraping (MCP)**
*   **Tool:** Python with `Crawl4AI` (Open Source) + Model Context Protocol (MCP)
*   **Why:** You can build a lightweight MCP server in Python that tracks your PostgreSQL/Supabase database. When an item crosses the 180-day unworn threshold, the agent triggers an open-source headless scraper to query Grailed or eBay to fetch current market pricing.

### 4. Feature Matrix (MVP Prioritization)

| MVP (Must-Haves) | Post-Launch (Nice-to-Haves) |
| :--- | :--- |
| One-click photo upload and auto-background removal. | Pinterest image integration and aesthetic matching. |
| VLM image processing to structured JSON metadata. | Closed-Loop Resale Agent (MCP web scraping). |
| Basic vector embedding generation and Pinecone storage. | Automated 1-click exporting/listing to eBay. |
| Weather-based filtering (Open-Meteo API). | Push notifications for unworn items. |

### 5. Next.js to Python Development Roadmap

Since you are transitioning from Python to full-stack, Next.js will serve purely as your user interface and API router, while Python handles the heavy lifting.

*   **Step 1: The Python AI Backend (Week 1)**
    *   Build a FastAPI server.
    *   Integrate `briaai/RMBG-1.4` for local background removal.
    *   Connect the Gemini 2.5 Flash API to process the cleaned images into JSON.
*   **Step 2: Vectorization & Storage (Week 2)**
    *   Write a Python script to convert the JSON metadata into vector embeddings.
    *   Set up your free Pinecone Starter tier and push the embeddings.
*   **Step 3: Next.js UI & Frontend (Week 3)**
    *   *Next.js Concept:* Use "Server Actions" to handle image uploads securely.
    *   Build a simple React interface where the user can snap a photo. 
    *   Route the uploaded photo from the Next.js frontend to your Python FastAPI backend.
*   **Step 4: The Recommendation Engine (Week 4)**
    *   Call the Open-Meteo API to fetch local temperature.
    *   Query Pinecone from your backend using the weather parameters and return the JSON payload to Next.js to display the curated outfit.

### 6. Budget Forecast

| Service | Purpose | Monthly Cost | Rationale |
| :--- | :--- | :--- | :--- |
| **Vercel** | Next.js Frontend Hosting | $0.00 | 1 million invocations and 100 daily deployments are free on Hobby tier. |
| **Pinecone** | Vector DB | $0.00 | Starter tier includes up to 100,000 vectors at no cost. |
| **Gemini API** | Vision LLM | $0.00 | Stays entirely within the 10 RPM / 250k TPM free tier limits. |
| **Open-Meteo** | Weather API | $0.00 | 10,000 calls per day are free for non-commercial use. |
| **Hugging Face** | BG Removal | $0.00 | Sourced locally using free, open-source model weights. |
| **Total Cost** | | **$0.00** | Architecture is highly scalable without triggering paid limits. |

**Session Continuity Summary for Part 2:**
*Project Loom is a digital wardrobe app utilizing Next.js (Vercel), Python (FastAPI), Pinecone (Free Starter Tier), Gemini 2.5 Flash API, and Open-Meteo. The pipeline removes backgrounds via `briaai/RMBG-1.4`, generates JSON tags via VLM, and recommends outfits using high-dimensional vector search. The MVP prioritizes tagging and weather recommendations over the secondary-market MCP scraper.*
