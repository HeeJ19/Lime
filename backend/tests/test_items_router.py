import base64

from app.routers import items
from app.services.vlm_tagging import TaggingError

_VALID_TAGS = {
    "category": "top",
    "silhouette": "oversized hoodie",
    "palette": ["heather grey", "black"],
    "texture": "brushed fleece",
    "aesthetic": "streetwear",
}


def _patch_pipeline(monkeypatch, *, tags=None, tagging_error=None, embed_error=None):
    monkeypatch.setattr(items, "remove_background", lambda raw: b"stripped-bytes")

    if tagging_error is not None:
        def _tag_image(stripped):
            raise tagging_error

        monkeypatch.setattr(items, "tag_image", _tag_image)
    else:
        from app.models.item_tags import ItemTags

        monkeypatch.setattr(items, "tag_image", lambda stripped: ItemTags(**(tags or _VALID_TAGS)))

    if embed_error is not None:
        def _embed(*a, **k):
            raise embed_error

        monkeypatch.setattr(items, "embed_and_store", _embed)
    else:
        monkeypatch.setattr(items, "embed_and_store", lambda *a, **k: None)


def test_ingest_success(client, monkeypatch):
    _patch_pipeline(monkeypatch)

    response = client.post(
        "/items/ingest",
        files={"file": ("photo.png", b"fake-image-bytes", "image/png")},
        data={"user_id": "user-123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tags"]["category"] == "top"
    assert base64.b64decode(body["stripped_image_base64"]) == b"stripped-bytes"


def test_ingest_missing_user_id_returns_422(client, monkeypatch):
    _patch_pipeline(monkeypatch)

    response = client.post(
        "/items/ingest",
        files={"file": ("photo.png", b"fake-image-bytes", "image/png")},
        data={"user_id": "  "},
    )

    assert response.status_code == 422


def test_ingest_non_image_file_returns_422(client, monkeypatch):
    _patch_pipeline(monkeypatch)

    response = client.post(
        "/items/ingest",
        files={"file": ("notes.txt", b"hello", "text/plain")},
        data={"user_id": "user-123"},
    )

    assert response.status_code == 422


def test_ingest_empty_file_returns_422(client, monkeypatch):
    _patch_pipeline(monkeypatch)

    response = client.post(
        "/items/ingest",
        files={"file": ("photo.png", b"", "image/png")},
        data={"user_id": "user-123"},
    )

    assert response.status_code == 422


def test_ingest_oversized_file_returns_422(client, monkeypatch):
    _patch_pipeline(monkeypatch)

    oversized = b"x" * (10 * 1024 * 1024 + 1)
    response = client.post(
        "/items/ingest",
        files={"file": ("photo.png", oversized, "image/png")},
        data={"user_id": "user-123"},
    )

    assert response.status_code == 422


def test_ingest_background_removal_failure_returns_502(client, monkeypatch):
    def _raise(raw):
        raise RuntimeError("model load failed")

    monkeypatch.setattr(items, "remove_background", _raise)

    response = client.post(
        "/items/ingest",
        files={"file": ("photo.png", b"fake-image-bytes", "image/png")},
        data={"user_id": "user-123"},
    )

    assert response.status_code == 502


def test_ingest_tagging_error_returns_502(client, monkeypatch):
    _patch_pipeline(monkeypatch, tagging_error=TaggingError("bad response"))

    response = client.post(
        "/items/ingest",
        files={"file": ("photo.png", b"fake-image-bytes", "image/png")},
        data={"user_id": "user-123"},
    )

    assert response.status_code == 502


def test_ingest_embedding_failure_returns_502(client, monkeypatch):
    _patch_pipeline(monkeypatch, embed_error=RuntimeError("pinecone down"))

    response = client.post(
        "/items/ingest",
        files={"file": ("photo.png", b"fake-image-bytes", "image/png")},
        data={"user_id": "user-123"},
    )

    assert response.status_code == 502
