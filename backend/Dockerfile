FROM python:3.11-slim

WORKDIR /app

# System libraries required by torch (libgomp) and Pillow/scikit-image
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libgomp1 libsm6 libxext6 libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first so this layer is cached independently
# of code changes (only re-runs when requirements.txt changes).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download both ML models at build time so they are baked into the image
# layer — eliminates the ~2 min cold-start that downloading them at first
# request would cause.
#
# briaai/RMBG-1.4: background removal (requires trust_remote_code=True for
# the custom transformers pipeline code; pinned at transformers==4.49.0 in
# requirements.txt — see background_removal.py for the reason).
RUN python -c "\
from transformers import pipeline; \
pipeline('image-segmentation', model='briaai/RMBG-1.4', trust_remote_code=True)"

# sentence-transformers/all-MiniLM-L6-v2: 384-dim embedding model for item
# tags and weather-query text (matches the Pinecone index dimensions).
RUN python -c "\
from sentence_transformers import SentenceTransformer; \
SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

COPY . .

EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
