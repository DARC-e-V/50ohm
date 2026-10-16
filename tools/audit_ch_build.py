"""Audit the first Swiss MDX/Astro build without altering canonical sources."""

import argparse
import hashlib
import json
from pathlib import Path

from prepare_ch_input import digest_tree

EDITIONS = ("NE", "A", "NEA")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changed_inputs(source: Path, state: dict) -> list[str]:
    sources = {
        "catalog": source / "contents/questions/fragenkatalog_4.json",
        "original_metadata": Path(state["source"]) / "contents/questions/metadata3b.json",
        "toc": source / "toc/HB.json",
    }
    changed = [name for name, path in sources.items() if digest(path) != state["input_sha256"][name]]
    for name, path in {
        "extra_content": Path(state["source"]) / "generator_extra_content",
        "snippets": Path(state["source"]) / "contents/snippets",
    }.items():
        if digest_tree(path) != state["input_sha256"][name]:
            changed.append(name)
    return changed


def audit(source: Path, build: Path, site: Path) -> dict:
    state = json.loads((source / "source-state.json").read_text(encoding="utf-8"))
    changed = changed_inputs(source, state)
    if changed:
        raise ValueError(f"Staged input changed since preparation: {changed}")

    questions = json.loads((build / "_data/questions.json").read_text(encoding="utf-8"))
    question_index = json.loads((build / "_data/question_index.json").read_text(encoding="utf-8"))
    if len(questions) != state["questions"]:
        raise ValueError(f"Question count changed: {len(questions)} instead of {state['questions']}")
    section_counts = {}
    for edition in EDITIONS:
        section_counts[edition] = len([
            path for path in (build / edition).glob("*/*.mdx") if path.name != "index.mdx"
        ])
        if section_counts[edition] != state["section_counts"][edition]:
            raise ValueError(f"Wrong section count for {edition}: {section_counts[edition]}")
        if not (site / edition / "index.html").is_file():
            raise FileNotFoundError(f"Missing Astro edition page: {edition}")
    for name in ("index.json", "question_index.json"):
        if not (site / "assets" / name).is_file():
            raise FileNotFoundError(f"Missing site search index: {name}")

    missing_drawings = sorted({
        entry["picture"]["id"]
        for question in questions.values()
        for entry in [question, *question["answers"]]
        if "picture" in entry and not (site / "pictures" / f"{entry['picture']['id']}.svg").is_file()
    })
    if missing_drawings:
        raise ValueError(f"Question pictures missing from site: {missing_drawings}")

    return {
        "content_commit": state["content_commit"],
        "question_commit": state["question_commit"],
        "questions": len(questions),
        "supplemental_metadata": len(state["supplemental_metadata"]),
        "section_counts": section_counts,
        "question_index_entries": len(question_index),
        "missing_referenced_questions": sorted(set(question_index) - set(questions)),
        "site_pages": len(list(site.rglob("index.html"))),
        "question_drawings": len(list((site / "pictures").glob("*.svg"))),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--strict-references", action="store_true")
    args = parser.parse_args()
    report = audit(args.source, args.build, args.site)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"questions": report["questions"], "section_counts": report["section_counts"],
                      "missing_referenced_questions": len(report["missing_referenced_questions"]),
                      "site_pages": report["site_pages"]}, ensure_ascii=False))
    if args.strict_references and report["missing_referenced_questions"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
