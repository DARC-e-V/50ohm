import pytest
import yaml
from ohm_builder.mdx_builder import frontmatter


@pytest.mark.mdx
def test_block_is_delimited_and_followed_by_a_blank_line():
    assert frontmatter({"title": "Rufzeichen"}) == "---\ntitle: Rufzeichen\n---\n\n"


@pytest.mark.mdx
def test_numbers_stay_unquoted():
    assert frontmatter({"chapterNumber": 1, "sectionNumber": 3}) == ("---\nchapterNumber: 1\nsectionNumber: 3\n---\n\n")


@pytest.mark.mdx
def test_none_values_are_omitted():
    assert frontmatter({"title": "Vorwort", "videoUrl": None}) == "---\ntitle: Vorwort\n---\n\n"


@pytest.mark.mdx
def test_umlauts_are_not_escaped():
    assert "Grundsätze" in frontmatter({"title": "Grundsätze"})


@pytest.mark.mdx
def test_key_order_is_kept():
    meta = {"title": "a", "ident": "b", "edition": "N", "chapterNumber": 1}
    lines = frontmatter(meta).splitlines()[1:-2]
    assert [line.split(":")[0] for line in lines] == list(meta)


@pytest.mark.mdx
def test_special_characters_round_trip():
    # Values that would break a naive serializer: a leading "-", a colon, quotes, a "#".
    meta = {
        "title": '- "Kurzwelle": alles #1',
        "videoUrl": "https://example.org/watch?v=a&t=1s",
        "ident": "yes",
    }
    block = frontmatter(meta)
    assert yaml.safe_load(block.removeprefix("---\n").removesuffix("---\n\n")) == meta
