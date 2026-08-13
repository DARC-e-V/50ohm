from pathlib import Path

import pytest
import yaml
from ohm_builder.config import Config
from ohm_builder.mdx_builder import MdxBuilder

FIXTURE_CONTENT = Path(__file__).parent / "fixtures" / "content"


def split_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path} has no frontmatter"
    end = text.index("\n---\n", 3)
    return yaml.safe_load(text[len("---\n") : end]), text[end + len("\n---\n") :]


@pytest.fixture
def build(tmp_path):
    """Builds the fixture edition and returns the output directory.

    The fixture content has no ``contents/slides/`` directory at all, so a builder that tried to
    read the slides would fail here.
    """
    config = Config(content_path=str(FIXTURE_CONTENT), build_path=str(tmp_path))
    builder = MdxBuilder(config)
    builder.build_edition("T")
    builder.build_question_index()
    builder.build_index()
    return tmp_path


@pytest.mark.builder
def test_editions_are_structured_in_folders(build):
    assert sorted(build.rglob("*.mdx")) == [
        build / "T" / "index.mdx",
        build / "T" / "t_erstes_kapitel/index.mdx",
        build / "T" / "t_erstes_kapitel/mit_video.mdx",
        build / "T" / "t_erstes_kapitel/ohne_video.mdx",
    ]


@pytest.mark.builder
def test_edition_index_carries_the_abstract_as_its_body(build):
    meta, body = split_frontmatter(build / "T" / "index.mdx")

    assert meta == {"title": "Testkurs T", "edition": "T"}
    assert body.strip() == "Ein Kurs, der nur in den Tests vorkommt."


@pytest.mark.builder
def test_chapter_index_carries_the_abstract_as_its_body(build):
    meta, body = split_frontmatter(build / "T" / "t_erstes_kapitel" / "index.mdx")

    assert meta == {
        "title": "Erstes Kapitel",
        "ident": "t_erstes_kapitel",
        "edition": "T",
        "chapterNumber": 1,
        "videoUrl": "https://example.org/watch?v=chapter&t=0s",
    }
    assert body.strip() == "Das Abstract des ersten Kapitels."


@pytest.mark.builder
def test_section_frontmatter_is_correct(build):
    meta, _ = split_frontmatter(build / "T" / "t_erstes_kapitel" / "mit_video.mdx")

    assert meta == {
        "title": "Mit Video",
        "ident": "mit_video",
        "edition": "T",
        "chapterIdent": "t_erstes_kapitel",
        "chapterNumber": 1,
        "sectionNumber": 1,
        "videoUrl": "https://example.org/watch?v=section&t=42s",
        "status": "prod",
        "class": "T",
    }


@pytest.mark.builder
def test_missing_video_url_is_omitted(build):
    meta, _ = split_frontmatter(build / "T" / "t_erstes_kapitel" / "ohne_video.mdx")

    assert "videoUrl" not in meta
    assert meta["sectionNumber"] == 2


@pytest.mark.builder
def test_questions_and_indices_stay_components(build):
    _, body = split_frontmatter(build / "T" / "t_erstes_kapitel" / "mit_video.mdx")

    # The frontend resolves these, so the builder must not render them itself.
    assert '<Question number="TF101" />' in body
    assert '<Index first="Rufzeichen" />' in body


@pytest.mark.builder
def test_includes_are_copied_with_their_pictures(build):
    _, body = split_frontmatter(build / "T" / "t_erstes_kapitel" / "ohne_video.mdx")

    # The renderer only emits the component, so the builder has to copy the files itself.
    assert '<Include ident="t_applet" />' in body
    assert (build / "includes" / "t_applet.html").exists()
    assert (build / "pictures" / "4711.svg").exists()


@pytest.mark.builder
def test_search_indices_land_in_the_data_folder(build):
    index = yaml.safe_load((build / "_data" / "index.json").read_text(encoding="utf-8"))
    question_index = yaml.safe_load((build / "_data" / "question_index.json").read_text(encoding="utf-8"))

    # The anchor ids are the same ones the HTML build emits, umlauts included.
    assert [(entry["term"], entry["subterm"], entry["anchor_id"]) for entry in index] == [
        ("Rufzeichen", None, "index_rufzeichen"),
        ("Rufzeichen", "Persönliches", "index_rufzeichen__persönliches"),
    ]
    assert question_index["TF101"]["editions"] == ["T"]
    assert question_index["TF101"]["section"] == "mit_video"


@pytest.mark.builder
def test_html_only_output_is_not_produced(build):
    assert not (build / "assets").exists()
    assert not (build / "index.html").exists()
    assert list(build.rglob("*.html")) == [build / "includes" / "t_applet.html"]
