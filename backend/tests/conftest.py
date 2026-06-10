import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.item_tags import ItemTags


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def sample_tags() -> ItemTags:
    return ItemTags(
        category="top",
        silhouette="oversized hoodie",
        palette=["heather grey", "black"],
        texture="brushed fleece",
        aesthetic="streetwear",
    )
