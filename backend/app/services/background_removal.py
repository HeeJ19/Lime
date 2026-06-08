"""Stage 1 of the ingestion pipeline: strip the background from an uploaded photo.

Uses `briaai/RMBG-1.4` via the `transformers` `image-segmentation` pipeline.
This model ships custom modeling code (no stock `transformers` architecture
matches it), so loading it requires `trust_remote_code=True` — the user has
explicitly authorized this. Pin `transformers==4.49.0` in requirements.txt:
the model's custom code references an internal attribute (`_tied_weights_keys`)
that newer `transformers` versions renamed, breaking the load.
"""

import io

from PIL import Image
from transformers import pipeline
from transformers.pipelines.base import Pipeline

_pipe: Pipeline | None = None


def _get_pipeline() -> Pipeline:
    global _pipe
    if _pipe is None:
        _pipe = pipeline("image-segmentation", model="briaai/RMBG-1.4", trust_remote_code=True)
    return _pipe


def remove_background(image_bytes: bytes) -> bytes:
    """Strip the background from a photo, returning a transparent PNG as bytes."""
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    result = _get_pipeline()(image)

    buffer = io.BytesIO()
    result.save(buffer, format="PNG")
    return buffer.getvalue()
