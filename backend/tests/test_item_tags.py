import pytest
from pydantic import ValidationError

from app.models.item_tags import ItemTags


def test_valid_tags_round_trip():
    tags = ItemTags(
        category="top",
        silhouette="  oversized hoodie  ",
        palette=["heather grey", " black "],
        texture="brushed fleece",
        aesthetic="streetwear",
    )

    assert tags.category == "top"
    assert tags.silhouette == "oversized hoodie"
    assert tags.palette == ["heather grey", "black"]


@pytest.mark.parametrize("category", ["jacket", "TOP", "", "tops"])
def test_rejects_invalid_category(category):
    with pytest.raises(ValidationError):
        ItemTags(
            category=category,
            silhouette="slim jeans",
            palette=["blue"],
            texture="denim",
            aesthetic="casual",
        )


@pytest.mark.parametrize("field", ["silhouette", "texture", "aesthetic"])
def test_rejects_blank_string_fields(field):
    payload = {
        "category": "bottom",
        "silhouette": "slim straight-leg jeans",
        "palette": ["blue"],
        "texture": "denim",
        "aesthetic": "casual",
        field: "   ",
    }

    with pytest.raises(ValidationError):
        ItemTags(**payload)


def test_palette_drops_blank_entries_but_keeps_real_colors():
    tags = ItemTags(
        category="shoes",
        silhouette="low-top sneakers",
        palette=["white", "  ", "", "red"],
        texture="canvas",
        aesthetic="athleisure",
    )

    assert tags.palette == ["white", "red"]


def test_palette_all_blank_is_rejected():
    with pytest.raises(ValidationError):
        ItemTags(
            category="shoes",
            silhouette="low-top sneakers",
            palette=["", "   "],
            texture="canvas",
            aesthetic="athleisure",
        )


def test_palette_must_be_a_list():
    with pytest.raises(ValidationError):
        ItemTags(
            category="shoes",
            silhouette="low-top sneakers",
            palette="white",
            texture="canvas",
            aesthetic="athleisure",
        )


def test_model_validate_json_rejects_malformed_json():
    with pytest.raises(ValidationError):
        ItemTags.model_validate_json("{not valid json")


def test_model_validate_json_rejects_missing_fields():
    with pytest.raises(ValidationError):
        ItemTags.model_validate_json('{"category": "top", "silhouette": "hoodie"}')
