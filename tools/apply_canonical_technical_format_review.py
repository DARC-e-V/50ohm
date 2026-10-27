"""Apply only explicitly approved, hash-checked technical-region corrections."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    from .technical_format_validation import technical_signature
except ImportError:  # Running this file directly places tools/ on sys.path.
    from technical_format_validation import technical_signature


REPO = Path(__file__).resolve().parents[1]
ORCHESTRATOR = REPO.parent
VALID_DECISIONS = {"", "apply", "keep", "manual"}
APPLICABLE_RECOMMENDATIONS = {
    "replace_with_german_region",
    "normalize_german_math_markup_preserve_locale_labels",
    "align_german_technical_markup",
}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _inside_root(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path escapes canonical root: {relative}")
    return path


def collect_changes(
    manifest_path: Path,
    decisions_path: Path,
    canonical_root: Path,
) -> tuple[dict[Path, list[dict[str, Any]]], list[dict[str, str]]]:
    canonical_root = canonical_root.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    proposals = {proposal["case_id"]: proposal for proposal in manifest.get("correction_proposals", [])}
    manual = {case["case_id"] for case in manifest.get("manual_review_cases", [])}
    localized = {case["case_id"] for case in manifest.get("localized_label_cases", [])}
    changes: dict[Path, list[dict[str, Any]]] = defaultdict(list)
    decisions: list[dict[str, str]] = []
    decision_by_case: dict[str, str] = {}
    seen: set[str] = set()

    with decisions_path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            case_id = row.get("case_id", "").strip()
            decision = row.get("decision", "").strip().lower()
            if not case_id:
                raise ValueError("Decision CSV contains a row without case_id")
            if case_id in seen:
                raise ValueError(f"Duplicate decision for case {case_id}")
            seen.add(case_id)
            if decision not in VALID_DECISIONS:
                raise ValueError(f"Invalid decision {decision!r} for case {case_id}")
            decision_by_case[case_id] = decision
            if not decision:
                continue
            decisions.append({"case_id": case_id, "decision": decision, "reviewer_note": row.get("reviewer_note", "")})
            if decision != "apply":
                if case_id not in proposals and case_id not in manual and case_id not in localized:
                    raise ValueError(f"Unknown review case {case_id}")
                continue
            proposal = proposals.get(case_id)
            if proposal is None or proposal.get("recommendation") not in APPLICABLE_RECOMMENDATIONS:
                raise ValueError(f"Case {case_id} is not an applicable correction proposal")
            target_path = _inside_root(canonical_root, proposal["target_file"])
            source_path = _inside_root(canonical_root, proposal["german_file"])
            changes[target_path].append({**proposal, "source_path": source_path})

    # A deterministic formatting difference is never a discretionary locale
    # choice: its canonical form is the German reference. Require the approved
    # German-form proposal to remain selected in the decisions file.
    for case_id, proposal in proposals.items():
        if proposal.get("priority") == "format_review" and decision_by_case.get(case_id) != "apply":
            raise ValueError(
                f"Format-equivalent case {case_id} must apply the German reference form; "
                "its decision cannot be blank, keep, or manual."
            )
    return changes, decisions


def prepare_outputs(changes: dict[Path, list[dict[str, Any]]]) -> dict[Path, tuple[str, str, list[dict[str, Any]]]]:
    outputs: dict[Path, tuple[str, str, list[dict[str, Any]]]] = {}
    for target_path, rows in changes.items():
        original = target_path.read_text(encoding="utf-8")
        source_by_hash: dict[tuple[str, str], list[str]] = {}
        operations = []
        for row in rows:
            if sha256_text(original) != row["target_sha256"]:
                raise ValueError(f"Target has changed since review: {target_path}")
            source_path = row["source_path"]
            source_text = source_path.read_text(encoding="utf-8")
            source_hash = row["german_sha256"]
            if sha256_text(source_text) != source_hash:
                raise ValueError(f"German reference has changed since review: {source_path}")
            key = (str(source_path), source_hash)
            if key not in source_by_hash:
                source_by_hash[key] = [region["text"] for region in technical_signature(source_text)["regions"]]
            index = int(row["region_index"])
            if index >= len(source_by_hash[key]) or source_by_hash[key][index] != row["german_text"]:
                raise ValueError(f"German reference region changed for case {row['case_id']}")
            if row.get("recommendation") == "align_german_technical_markup":
                try:
                    from .technical_markup_repairs import plan_markup_repairs
                except ImportError:
                    from technical_markup_repairs import plan_markup_repairs
                replayed, details = plan_markup_repairs(source_text, original, row["language"])
                if replayed != row["proposed_text"] or details != row["markup_operations"]:
                    raise ValueError(f"Markup plan cannot be reproduced for case {row['case_id']}")
            start = int(row["target_payload_start"])
            end = int(row["target_payload_end"])
            expected = row["current_text"]
            if start < 0 or end < start or original[start:end] != expected:
                raise ValueError(f"Target span changed for case {row['case_id']}")
            operations.append(
                {
                    "case_id": row["case_id"],
                    "start": start,
                    "end": end,
                    "expected": expected,
                    "replacement": row.get("proposed_text", row["german_text"]),
                    "finding_category": row["finding_category"],
                    **({"markup_operations": row["markup_operations"]} if "markup_operations" in row else {}),
                }
            )

        operations.sort(key=lambda operation: (operation["start"], operation["end"]), reverse=True)
        for previous, current in zip(operations, operations[1:]):
            if current["end"] > previous["start"]:
                raise ValueError(f"Approved correction spans overlap in {target_path}")
        updated = original
        for operation in operations:
            updated = updated[: operation["start"]] + operation["replacement"] + updated[operation["end"] :]
        outputs[target_path] = (original, updated, operations)
    return outputs


def _atomic_write(path: Path, text: str) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".review-tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def apply_review(
    manifest_path: Path,
    decisions_path: Path,
    canonical_root: Path,
    applied_manifest: Path,
    apply: bool,
) -> dict[str, Any]:
    changes, decisions = collect_changes(manifest_path, decisions_path, canonical_root)
    outputs = prepare_outputs(changes)
    if apply:
        for path, (_, updated, _) in outputs.items():
            _atomic_write(path, updated)

    result = {
        "schema_version": 1,
        "tool": "apply_canonical_technical_format_review",
        "mode": "applied" if apply else "dry_run",
        "review_manifest": str(manifest_path.resolve()),
        "review_manifest_sha256": sha256_file(manifest_path),
        "decisions_csv": str(decisions_path.resolve()),
        "decisions_csv_sha256": sha256_file(decisions_path),
        "files": [
            {
                "path": path.relative_to(canonical_root.resolve()).as_posix(),
                "before_sha256": sha256_text(original),
                "after_sha256": sha256_text(updated),
                "changes": operations,
            }
            for path, (original, updated, operations) in sorted(outputs.items(), key=lambda item: str(item[0]))
        ],
        "decisions": decisions,
        "approved_case_count": sum(decision["decision"] == "apply" for decision in decisions),
    }
    applied_manifest.parent.mkdir(parents=True, exist_ok=True)
    applied_manifest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True, help="JSON manifest produced by the comparison tool")
    parser.add_argument("--decisions-csv", type=Path, required=True, help="Human-reviewed case_id/decision CSV")
    parser.add_argument("--canonical-root", type=Path, default=REPO.parent / "50ohm-contents-ch" / "canonical")
    parser.add_argument("--applied-manifest", type=Path, default=ORCHESTRATOR / "tmp" / "canonical-technical-format-applied.json")
    parser.add_argument("--apply", action="store_true", help="Write approved corrections; without it, perform a dry run")
    args = parser.parse_args()

    result = apply_review(args.manifest, args.decisions_csv, args.canonical_root, args.applied_manifest, args.apply)
    print(f"mode={result['mode']}")
    print(f"approved_cases={result['approved_case_count']}")
    print(f"files={len(result['files'])}")
    print(f"manifest={args.applied_manifest.resolve()}")


if __name__ == "__main__":
    main()
