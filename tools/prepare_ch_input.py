"""Prepare a Swiss MDX input from one localized canonical generator export.

The source is read-only. A fresh, ignored directory holds the derived question
metadata and links to the exported course assets.
"""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from jinja2 import Environment, StrictUndefined
from ohm_renderer.document import Document
from ohm_renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer

LANGUAGES = ("de", "fr", "it")
EDITIONS = ("NE", "A", "NEA")
PICTURE_FIELDS = ("picture_question", "picture_a", "picture_b", "picture_c", "picture_d")
EXTRA_HTML_PAGES = ("index", "kurse-karte", "kurse-liste", "patenkarte", "todo")


def questions_in(pool: dict):
    for part in pool["sections"]:
        for chapter in part["sections"]:
            yield from chapter.get("questions", [])
            for section in chapter.get("sections", []):
                yield from section["questions"]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_tree(root: Path) -> str:
    hasher = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            hasher.update(str(path.relative_to(root)).encode())
            hasher.update(path.read_bytes())
    return hasher.hexdigest()


def render_extra_pages(source: Path, output: Path, language: str) -> None:
    """Render extracted Jinja pages with current canonical snippets."""
    snippets = {}
    with FiftyOhmHtmlRenderer() as renderer:
        for path in (source / "contents" / "snippets").glob("*.md"):
            html = renderer.render_inner(Document(path.read_text(encoding="utf-8"))).strip()
            snippets[path.stem] = html[3:-4] if html.startswith("<p>") and html.endswith("</p>") else html

    templates = source / "generator_extra_content" / language / "templates" / "html"
    rendered = output / "rendered_extra_content" / "html"
    rendered.mkdir(parents=True)
    env = Environment(undefined=StrictUndefined, autoescape=False)
    for name in EXTRA_HTML_PAGES:
        template = (templates / f"{name}.html").read_text(encoding="utf-8")
        page = env.from_string(template).render(snippets=snippets) + "\n"
        (rendered / f"{name}.html").write_text(page, encoding="utf-8")


def revision(path: Path) -> str:
    return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()


def complete_metadata(question_list: list[dict], original_metadata: dict, drawings: Path) -> tuple[dict, list[str]]:
    metadata = {}
    supplemental = []
    missing_pictures = []
    for question in question_list:
        number = question["number"]
        existing = original_metadata.get(number)
        if existing is None:
            supplemental.append(number)
        item = dict(existing or {})
        item.setdefault("layout", "")
        for field in PICTURE_FIELDS:
            value = item.get(field) or question.get(field) or ""
            item[field] = str(value)
            if value and not (drawings / f"{value}.svg").is_file():
                missing_pictures.append(f"{number}:{field}:{value}")
        metadata[number] = item
    if missing_pictures:
        raise ValueError(f"Question drawings missing from source: {missing_pictures}")
    return metadata, supplemental


def count_sections(toc: dict) -> dict[str, int]:
    classes = [section["class"] for chapter in toc["chapters"] for section in chapter["sections"]]
    invalid_classes = sorted(set(classes) - set("NEA"))
    if invalid_classes:
        raise ValueError(f"Unknown section classes in HB.json: {invalid_classes}")
    return {edition: sum(cls in edition for cls in classes) for edition in EDITIONS}


def prepare(source: Path, output: Path, language: str, content_repo: Path, question_repo: Path) -> dict:
    if language not in LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")
    source = source.resolve(strict=True)
    output = output.absolute()
    if output.exists():
        raise FileExistsError(f"Use a new output directory: {output}")

    question_dir = source / "contents" / "questions"
    catalog_path = question_dir / "fragenkatalog_4.json"
    original_metadata_path = question_dir / "metadata3b.json"
    toc_path = source / "toc" / "HB.json"
    pool = json.loads(catalog_path.read_text(encoding="utf-8"))
    original_metadata = json.loads(original_metadata_path.read_text(encoding="utf-8"))
    toc = json.loads(toc_path.read_text(encoding="utf-8"))
    question_list = list(questions_in(pool))
    numbers = [question["number"] for question in question_list]
    if len(numbers) != len(set(numbers)):
        raise ValueError("Duplicate question numbers in the current catalog")

    metadata, supplemental = complete_metadata(question_list, original_metadata, source / "contents" / "drawings")
    section_counts = count_sections(toc)

    # Do not duplicate the large source trees; the prototype links to the current export.
    (output / "contents" / "questions").mkdir(parents=True)
    (output / "toc").mkdir()
    (output / "toc" / "HB.json").symlink_to(toc_path)
    (output / "generator_extra_content").symlink_to((source / "generator_extra_content").resolve(strict=True))
    for directory in (source / "contents").iterdir():
        if directory.name != "questions":
            (output / "contents" / directory.name).symlink_to(directory.resolve())
    (output / "contents" / "questions" / "fragenkatalog_4.json").symlink_to(catalog_path)
    (output / "contents" / "questions" / "metadata3b.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    render_extra_pages(source, output, language)
    details = {}
    for edition in EDITIONS:
        original = json.loads((source / "toc" / f"{edition}.json").read_text(encoding="utf-8"))
        details[edition] = {"title": original["title"], "abstract": original["abstract"]}
    (output / "build-config.json").write_text(
        json.dumps({"questions": "fragenkatalog_4.json", "toc_source": "HB.json", "edition_details": details},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    report = {
        "language": language,
        "source": str(source),
        "content_commit": revision(content_repo),
        "question_commit": revision(question_repo),
        "input_sha256": {
            "catalog": digest(catalog_path),
            "original_metadata": digest(original_metadata_path),
            "toc": digest(toc_path),
            "extra_content": digest_tree(source / "generator_extra_content"),
            "snippets": digest_tree(source / "contents" / "snippets"),
        },
        "questions": len(question_list),
        "supplemental_metadata": supplemental,
        "section_counts": section_counts,
    }
    (output / "source-state.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Fresh localized generator input")
    parser.add_argument("--language", choices=LANGUAGES, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New ignored output directory")
    parser.add_argument("--content-repo", type=Path, required=True)
    parser.add_argument("--question-repo", type=Path, required=True)
    args = parser.parse_args()
    report = prepare(args.source, args.output, args.language, args.content_repo, args.question_repo)
    print(json.dumps({"language": args.language, "output": str(args.output.absolute()), "questions": report["questions"],
                      "supplemental_metadata": len(report["supplemental_metadata"]),
                      "section_counts": report["section_counts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
