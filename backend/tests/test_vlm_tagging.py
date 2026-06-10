import httpx
import pytest

from app.services import vlm_tagging
from app.services.vlm_tagging import TaggingError, tag_image

_VALID_TAGS_JSON = (
    '{"category": "top", "silhouette": "oversized hoodie", '
    '"palette": ["heather grey", "black"], "texture": "brushed fleece", '
    '"aesthetic": "streetwear"}'
)


class _FakeResponse:
    def __init__(self, candidate_text):
        self._candidate_text = candidate_text

    def raise_for_status(self):
        pass

    def json(self):
        return {"candidates": [{"content": {"parts": [{"text": self._candidate_text}]}}]}


@pytest.fixture(autouse=True)
def _gemini_api_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")


def test_tag_image_returns_validated_tags(monkeypatch):
    monkeypatch.setattr(
        vlm_tagging.httpx, "post", lambda *a, **k: _FakeResponse(_VALID_TAGS_JSON)
    )

    tags = tag_image(b"fake-image-bytes")

    assert tags.category == "top"
    assert tags.aesthetic == "streetwear"


def test_tag_image_strips_markdown_code_fences(monkeypatch):
    fenced = f"```json\n{_VALID_TAGS_JSON}\n```"
    monkeypatch.setattr(vlm_tagging.httpx, "post", lambda *a, **k: _FakeResponse(fenced))

    tags = tag_image(b"fake-image-bytes")

    assert tags.category == "top"


def test_tag_image_raises_on_malformed_json(monkeypatch):
    monkeypatch.setattr(
        vlm_tagging.httpx, "post", lambda *a, **k: _FakeResponse("{not valid json")
    )

    with pytest.raises(TaggingError):
        tag_image(b"fake-image-bytes")


def test_tag_image_raises_on_schema_violation(monkeypatch):
    bad_json = '{"category": "hat", "silhouette": "cap", "palette": ["red"], "texture": "wool", "aesthetic": "casual"}'
    monkeypatch.setattr(vlm_tagging.httpx, "post", lambda *a, **k: _FakeResponse(bad_json))

    with pytest.raises(TaggingError):
        tag_image(b"fake-image-bytes")


def test_tag_image_raises_on_http_error(monkeypatch):
    def _raise(*a, **k):
        raise httpx.ConnectError("boom")

    monkeypatch.setattr(vlm_tagging.httpx, "post", _raise)

    with pytest.raises(TaggingError):
        tag_image(b"fake-image-bytes")


def test_tag_image_raises_on_unexpected_response_shape(monkeypatch):
    class _EmptyResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"candidates": []}

    monkeypatch.setattr(vlm_tagging.httpx, "post", lambda *a, **k: _EmptyResponse())

    with pytest.raises(TaggingError):
        tag_image(b"fake-image-bytes")
