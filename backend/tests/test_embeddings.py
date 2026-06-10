from app.models.item_tags import ItemTags
from app.services.embeddings import _tags_to_text


def test_tags_to_text_renders_descriptive_sentence():
    tags = ItemTags(
        category="top",
        silhouette="oversized hoodie",
        palette=["heather grey", "black"],
        texture="brushed fleece",
        aesthetic="streetwear",
    )

    text = _tags_to_text(tags)

    assert text == (
        "A oversized hoodie in heather grey and black, with a brushed fleece texture, "
        "styled as streetwear."
    )


def test_tags_to_text_with_single_color_palette_has_no_dangling_and():
    tags = ItemTags(
        category="bottom",
        silhouette="slim straight-leg jeans",
        palette=["indigo"],
        texture="denim",
        aesthetic="casual",
    )

    text = _tags_to_text(tags)

    assert text == "A slim straight-leg jeans in indigo, with a denim texture, styled as casual."
