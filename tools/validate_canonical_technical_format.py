"""Compare and prepare traceable technical-format corrections for canonical content."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

try:
    from .technical_format_validation import (
        body_inventory,
        classify_pair,
        localized_math_label_relation,
        same_measurement_with_bit_capitalization,
        technical_signature,
        technical_tokens_equivalent,
    )
except ImportError:  # Running this file directly places tools/ on sys.path.
    from technical_format_validation import (
        body_inventory,
        classify_pair,
        localized_math_label_relation,
        same_measurement_with_bit_capitalization,
        technical_signature,
        technical_tokens_equivalent,
    )


REPO = Path(__file__).resolve().parents[1]
ORCHESTRATOR = REPO.parent
try:
    from .technical_markup_repairs import plan_markup_repairs
except ImportError:
    from technical_markup_repairs import plan_markup_repairs


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _region_alignment(source: dict[str, Any], target: dict[str, Any]) -> bool:
    source_regions = source["regions"]
    target_regions = target["regions"]
    return len(source_regions) == len(target_regions) and all(
        (left["kind"], left["delimiter"]) == (right["kind"], right["delimiter"])
        for left, right in zip(source_regions, target_regions, strict=True)
    )


def _contains_region_swap(source: dict[str, Any], target: dict[str, Any]) -> bool:
    source_regions = source["regions"]
    target_regions = target["regions"]
    for left in range(len(source_regions)):
        for right in range(left + 1, len(source_regions)):
            if (
                technical_tokens_equivalent(source_regions[left]["tokens"], target_regions[right]["tokens"])
                and technical_tokens_equivalent(source_regions[right]["tokens"], target_regions[left]["tokens"])
                and not technical_tokens_equivalent(source_regions[left]["tokens"], source_regions[right]["tokens"])
            ):
                return True
    return False


def _case_id(target_file: str, start: int, source_text: str, target_text: str) -> str:
    payload = "\0".join((target_file, str(start), source_text, target_text))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _context(text: str, start: int, end: int, radius: int = 100) -> str:
    return " ".join(text[max(0, start - radius) : min(len(text), end + radius)].split())


def _critical_explanation(source: list[str], target: list[str]) -> str:
    numeric = re.compile(r"^[+-]?\d+(?:[.,]\d+)*(?:[eE][+-]?\d+)?$")
    source_numbers = [token for token in source if numeric.fullmatch(token)]
    target_numbers = [token for token in target if numeric.fullmatch(token)]
    source_commands = [token for token in source if token.startswith("\\")]
    target_commands = [token for token in target if token.startswith("\\")]
    if source_numbers != target_numbers and source_commands != target_commands:
        reason = "Both numeric values and LaTeX/unit commands differ; verify the quantity and unit before accepting the German replacement."
    elif source_numbers != target_numbers:
        reason = "A numeric value differs; check whether this is a translation error or an intentional conversion."
    elif source_commands != target_commands:
        reason = "A LaTeX command or unit representation differs; check equivalence and the required notation."
    else:
        reason = "A variable, symbol or descriptive label differs; this may be localized notation, so validate before copying German."
    return f"{reason} German tokens: {source!r}; target tokens: {target!r}."


def _manual_details(
    source_text: str,
    target_text: str,
    source: dict[str, Any],
    target: dict[str, Any],
) -> tuple[str, str, str, str]:
    source_regions = source["regions"]
    target_regions = target["regions"]
    differences = []
    for index in range(max(len(source_regions), len(target_regions))):
        left = source_regions[index] if index < len(source_regions) else None
        right = target_regions[index] if index < len(target_regions) else None
        if left and right and left["text"] == right["text"] and left["kind"] == right["kind"] and left["delimiter"] == right["delimiter"]:
            continue
        differences.append((index, left, right))
    if not differences and target["syntax_findings"]:
        for finding in target["syntax_findings"]:
            offset = int(finding.get("offset", 0))
            differences.append((offset, None, {"text": json.dumps(finding, ensure_ascii=False), "start": offset, "end": offset}))

    german_fragments = []
    target_fragments = []
    german_contexts = []
    target_contexts = []
    for index, left, right in differences[:12]:
        german_fragments.append(f"[{index}] {left['text']}" if left else f"[{index}] <absent>")
        target_fragments.append(f"[{index}] {right['text']}" if right else f"[{index}] <absent>")
        if left:
            german_contexts.append(f"[{index}] {_context(source_text, left['start'], left['end'], 70)}")
        if right:
            target_contexts.append(f"[{index}] {_context(target_text, right['start'], right['end'], 70)}")
    if len(differences) > 12:
        german_fragments.append(f"… and {len(differences) - 12} more differing regions")
        target_fragments.append(f"… and {len(differences) - 12} more differing regions")
    return (
        "\n".join(german_fragments),
        "\n".join(target_fragments),
        "\n".join(german_contexts),
        "\n".join(target_contexts),
    )


def validate(canonical_root: Path, default_locale: str, locales: list[str], *, markup_only: bool = False) -> dict[str, Any]:
    canonical_root = canonical_root.resolve()
    inventory = body_inventory(canonical_root)
    exceptions: list[dict[str, Any]] = []
    proposals: list[dict[str, Any]] = []
    manual_cases: list[dict[str, Any]] = []
    localized_label_cases: list[dict[str, Any]] = []
    markup_proposals: list[dict[str, Any]] = []
    compared_pairs = 0
    compared_objects: set[str] = set()
    exception_pairs = 0
    localized_only_pairs: set[tuple[str, str]] = set()
    target_locales = [locale for locale in locales if locale != default_locale]

    for (object_path, extension), variants in sorted(inventory.items()):
        german_path = variants.get(default_locale)
        for locale in target_locales:
            target_path = variants.get(locale)
            if german_path is None:
                continue
            if target_path is None:
                missing = {
                    "case_id": _case_id(_relative(german_path, canonical_root), 0, "missing_translation", locale),
                    "category": "missing_translation_body",
                    "priority": "critical_human_review",
                    "decision": "manual_review",
                    "object_path": object_path,
                    "body_extension": extension,
                    "language": locale,
                    "german_file": _relative(german_path, canonical_root),
                    "german_text": "German source exists; target body is absent.",
                    "current_text": "",
                    "recommendation": "create_or_confirm_translation_body",
                    "explanation": "The configured language has no canonical body for this object.",
                }
                exceptions.append(missing)
                manual_cases.append(missing.copy())
                continue

            compared_pairs += 1
            compared_objects.add(object_path)
            source_text = german_path.read_text(encoding="utf-8")
            target_text = target_path.read_text(encoding="utf-8")
            source = technical_signature(source_text)
            target = technical_signature(target_text)
            repaired, operations = plan_markup_repairs(source_text, target_text, locale)
            if operations:
                reference_index = operations[0]["reference_region_index"]
                reference = source["regions"][reference_index]
                markup_proposals.append({
                    "case_id": _case_id(_relative(target_path, canonical_root), 0, "markup:" + source["sha256"], target["sha256"]),
                    "finding_category": "technical_markup_mismatch", "priority": "format_review", "decision": "pending",
                    "codex_recommendation": "apply_source_backed_markup",
                    "language": locale, "object_path": object_path, "body_extension": extension,
                    "german_file": _relative(german_path, canonical_root), "target_file": _relative(target_path, canonical_root),
                    "german_sha256": source["sha256"], "target_sha256": target["sha256"],
                    "region_index": reference_index, "region_kind": reference["kind"], "delimiter": reference["delimiter"],
                    "german_text": reference["text"], "current_text": target_text, "proposed_text": repaired,
                    "target_payload_start": 0, "target_payload_end": len(target_text),
                    "recommendation": "align_german_technical_markup", "markup_operations": operations,
                    "explanation": "Source-backed markup corrections; preserve prose, values and localized formula labels. Detailed operations are recorded in the manifest.",
                })
            category = classify_pair(source, target)
            base_record = {
                "category": category,
                "object_path": object_path,
                "body_extension": extension,
                "language": locale,
                "german_file": _relative(german_path, canonical_root),
                "target_file": _relative(target_path, canonical_root),
                "german_sha256": source["sha256"],
                "target_sha256": target["sha256"],
                "german_technical_token_count": len(source["technical_tokens"]),
                "target_technical_token_count": len(target["technical_tokens"]),
            }
            if category == "match":
                continue

            if category == "localized_formula_label":
                localized_only_pairs.add((object_path, locale))
                for region_index, (source_region, target_region) in enumerate(
                    zip(source["regions"], target["regions"], strict=True)
                ):
                    relation = localized_math_label_relation(source_region["text"], target_region["text"])
                    if not relation:
                        continue
                    localized_label_cases.append(
                        {
                            "case_id": _case_id(
                                base_record["target_file"], target_region["payload_start"],
                                source_region["text"], target_region["text"],
                            ),
                            "category": "localized_formula_label",
                            "finding_category": "localized_formula_label",
                            "priority": "locale_label_keep",
                            "decision": "keep",
                            "codex_recommendation": "keep_translated_label",
                            **{key: base_record[key] for key in (
                                "language", "object_path", "body_extension", "german_file", "target_file",
                                "german_sha256", "target_sha256",
                            )},
                            "region_index": region_index,
                            "region_kind": source_region["kind"],
                            "delimiter": source_region["delimiter"],
                            "german_text": source_region["text"],
                            "current_text": target_region["text"],
                            "target_payload_start": target_region["payload_start"],
                            "target_payload_end": target_region["payload_end"],
                            "german_context": _context(source_text, source_region["start"], source_region["end"]),
                            "current_context": _context(target_text, target_region["start"], target_region["end"]),
                            "recommendation": "keep_translated_math_label",
                            "explanation": "Only language text inside matched math-label arguments differs; keeping the translated label preserves the target language.",
                        }
                    )
                continue

            exception_pairs += 1
            exceptions.append({**base_record, "german": source, "target": target})
            can_pair_regions = _region_alignment(source, target) and not _contains_region_swap(source, target) and category not in {
                "same_technical_tokens_different_order",
                "same_technical_tokens_different_boundaries",
                "malformed_technical_markup",
            }

            if can_pair_regions:
                for region_index, (source_region, target_region) in enumerate(
                    zip(source["regions"], target["regions"], strict=True)
                ):
                    if source_region["text"] == target_region["text"]:
                        continue
                    label_relation = localized_math_label_relation(source_region["text"], target_region["text"])
                    if label_relation:
                        case = {
                            "case_id": _case_id(
                                base_record["target_file"], target_region["payload_start"],
                                source_region["text"], target_region["text"],
                            ),
                            "category": "localized_formula_label",
                            "finding_category": "localized_formula_label",
                            "priority": "locale_label_keep",
                            "decision": "keep",
                            "codex_recommendation": "keep_translated_label",
                            **{key: base_record[key] for key in (
                                "language", "object_path", "body_extension", "german_file", "target_file",
                                "german_sha256", "target_sha256",
                            )},
                            "region_index": region_index,
                            "region_kind": source_region["kind"],
                            "delimiter": source_region["delimiter"],
                            "german_text": source_region["text"],
                            "current_text": target_region["text"],
                            "target_payload_start": target_region["payload_start"],
                            "target_payload_end": target_region["payload_end"],
                            "german_context": _context(source_text, source_region["start"], source_region["end"]),
                            "current_context": _context(target_text, target_region["start"], target_region["end"]),
                            "recommendation": "keep_translated_math_label",
                            "explanation": "The changed tokens are words inside matched math-label arguments; keep the translated label.",
                        }
                        if not label_relation["command_style_differs"]:
                            localized_label_cases.append(case)
                            continue
                        proposals.append(
                            {
                                **case,
                                "finding_category": "localized_label_markup_mismatch",
                                "priority": "format_review",
                                "decision": "pending",
                                "proposed_text": label_relation["proposed_text"],
                                "recommendation": "normalize_german_math_markup_preserve_locale_labels",
                                "explanation": "The translated labels are retained while their LaTeX wrappers are aligned to German.",
                            }
                        )
                        continue
                    if same_measurement_with_bit_capitalization(source_region["text"], target_region["text"]):
                        localized_label_cases.append(
                            {
                                "case_id": _case_id(
                                    base_record["target_file"], target_region["payload_start"],
                                    source_region["text"], target_region["text"],
                                ),
                                "category": "localized_unit_word_case",
                                "finding_category": "localized_unit_word_case",
                                "priority": "locale_label_keep",
                                "decision": "keep",
                                "codex_recommendation": "keep_localized_unit_word",
                                **{key: base_record[key] for key in (
                                    "language", "object_path", "body_extension", "german_file", "target_file",
                                    "german_sha256", "target_sha256",
                                )},
                                "region_index": region_index,
                                "region_kind": source_region["kind"],
                                "delimiter": source_region["delimiter"],
                                "german_text": source_region["text"],
                                "current_text": target_region["text"],
                                "target_payload_start": target_region["payload_start"],
                                "target_payload_end": target_region["payload_end"],
                                "german_context": _context(source_text, source_region["start"], source_region["end"]),
                                "current_context": _context(target_text, target_region["start"], target_region["end"]),
                                "recommendation": "keep_locale_specific_unit_word_case",
                                "explanation": "The numeric value and unit are identical; capitalization of the word ‘bit’ follows the target language.",
                            }
                        )
                        continue
                    tokens_match = technical_tokens_equivalent(source_region["tokens"], target_region["tokens"])
                    proposals.append(
                        {
                            "case_id": _case_id(
                                base_record["target_file"],
                                target_region["payload_start"],
                                source_region["text"],
                                target_region["text"],
                            ),
                            "finding_category": "technical_format_mismatch" if tokens_match else "technical_token_mismatch",
                            "priority": "format_review" if tokens_match else "critical_human_review",
                            "decision": "pending",
                            "codex_recommendation": "apply_after_critical_review" if tokens_match else "human_validation_required",
                            **{key: base_record[key] for key in (
                                "language", "object_path", "body_extension", "german_file", "target_file",
                                "german_sha256", "target_sha256",
                            )},
                            "region_index": region_index,
                            "region_kind": source_region["kind"],
                            "delimiter": source_region["delimiter"],
                            "german_text": source_region["text"],
                            "current_text": target_region["text"],
                            "proposed_text": source_region["text"],
                            "german_context": _context(source_text, source_region["start"], source_region["end"]),
                            "current_context": _context(target_text, target_region["start"], target_region["end"]),
                            "target_payload_start": target_region["payload_start"],
                            "target_payload_end": target_region["payload_end"],
                            "recommendation": "replace_with_german_region",
                            "explanation": (
                                "The technical tokens match, but the exact notation text differs."
                                if tokens_match
                                else _critical_explanation(source_region["tokens"], target_region["tokens"])
                            ),
                        }
                    )
            else:
                german_fragments, target_fragments, german_contexts, target_contexts = _manual_details(
                    source_text, target_text, source, target
                )
                manual_cases.append(
                    {
                        "case_id": _case_id(base_record["target_file"], 0, category, target["sha256"]),
                        "finding_category": category,
                        "priority": "critical_human_review",
                        "decision": "manual_review",
                        **{key: base_record[key] for key in (
                            "language", "object_path", "body_extension", "german_file", "target_file",
                            "german_sha256", "target_sha256",
                        )},
                        "german_text": german_fragments,
                        "current_text": target_fragments,
                        "german_context": german_contexts,
                        "current_context": target_contexts,
                        "recommendation": "manual_review",
                        "explanation": "The technical regions cannot be paired one-to-one without a human decision.",
                    }
                )

    # Report translated bodies which have no German counterpart.
    for (object_path, extension), variants in sorted(inventory.items()):
        if default_locale in variants:
            continue
        for locale in target_locales:
            if locale not in variants:
                continue
            missing = {
                "case_id": _case_id(_relative(variants[locale], canonical_root), 0, "missing_german_source", locale),
                "category": "missing_german_source_body",
                "priority": "critical_human_review",
                "decision": "manual_review",
                "object_path": object_path,
                "body_extension": extension,
                "language": locale,
                "target_file": _relative(variants[locale], canonical_root),
                "german_text": "",
                "current_text": "Target body exists without a German reference.",
                "recommendation": "manual_review",
                "explanation": "No German source body is available for comparison.",
            }
            exceptions.append(missing)
            manual_cases.append(missing.copy())

    markup_files = {item["target_file"] for item in markup_proposals}
    proposals = [*markup_proposals, *[item for item in proposals if not markup_only and item["target_file"] not in markup_files]]
    counts: dict[str, int] = {}
    for item in exceptions:
        category = str(item["category"])
        counts[category] = counts.get(category, 0) + 1
    counts_by_language: dict[str, dict[str, int]] = {}
    for item in exceptions:
        language = str(item.get("language", "unknown"))
        category = str(item["category"])
        language_counts = counts_by_language.setdefault(language, {})
        language_counts[category] = language_counts.get(category, 0) + 1
    return {
        "schema_version": 2,
        "tool": "validate_canonical_technical_format",
        "scope": {
            "canonical_root": "canonical/",
            "body_files": "body.{locale}.{md|html}",
            "reference_locale": default_locale,
            "target_locales": target_locales,
            "method": "ordered technical regions, exact region text and token comparison; proposals do not edit sources",
            "markup_only": markup_only,
        },
        "summary": {
            "objects_compared": len(compared_objects),
            "body_pairs_compared": compared_pairs,
            "matches": compared_pairs - exception_pairs,
            "exact_matches": compared_pairs - exception_pairs - len(localized_only_pairs),
            "localized_label_only_pairs": len(localized_only_pairs),
            "exception_count": len(exceptions),
            "exceptions_by_category": dict(sorted(counts.items())),
            "exceptions_by_language": {language: dict(sorted(values.items())) for language, values in sorted(counts_by_language.items())},
            "correction_proposal_count": len(proposals),
            "markup_repair_files": len(markup_proposals),
            "markup_repair_operations": sum(len(item["markup_operations"]) for item in markup_proposals),
            "format_review_count": sum(item["priority"] == "format_review" for item in proposals),
            "critical_proposal_count": sum(item["priority"] == "critical_human_review" for item in proposals),
            "manual_review_count": len(manual_cases),
            "localized_formula_label_count": sum(
                item.get("category") == "localized_formula_label" for item in localized_label_cases
            ),
            "localized_unit_word_case_count": sum(
                item.get("category") == "localized_unit_word_case" for item in localized_label_cases
            ),
        },
        "exceptions": exceptions,
        "correction_proposals": proposals,
        "manual_review_cases": manual_cases,
        "localized_label_cases": localized_label_cases,
    }


def write_review_csv(report: dict[str, Any], path: Path, items: list[dict[str, Any]] | None = None) -> None:
    fields = [
        "case_id", "finding_category", "priority", "codex_recommendation", "language", "object_path",
        "german_file", "target_file", "german_sha256", "target_sha256", "region_index",
        "region_kind", "delimiter", "german_text", "current_text", "proposed_text", "german_context", "current_context", "target_payload_start",
        "target_payload_end", "recommendation", "explanation",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        rows = items if items is not None else [
            *report["correction_proposals"], *report["manual_review_cases"], *report["localized_label_cases"]
        ]
        for item in rows:
            row = dict(item)
            row.setdefault("finding_category", row.get("category", ""))
            # Text columns are for display only; neutralize spreadsheet formulas.
            for field in ("german_text", "current_text", "proposed_text", "german_context", "current_context", "explanation"):
                value = row.get(field)
                if isinstance(value, str) and value.startswith(("=", "+", "-", "@", "\t", "\r")):
                    row[field] = "'" + value
            writer.writerow(row)


def write_decisions_csv(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["case_id", "decision", "reviewer_note"])
        writer.writeheader()
        for item in [*report["correction_proposals"], *report["manual_review_cases"], *report["localized_label_cases"]]:
            if item.get("priority") == "format_review":
                default_decision = "apply"
            elif item.get("priority") == "locale_label_keep":
                default_decision = "keep"
            else:
                default_decision = ""
            writer.writerow({"case_id": item["case_id"], "decision": default_decision, "reviewer_note": ""})


def _git_snapshot(path: Path) -> dict[str, Any]:
    commit = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True, check=False
    )
    root = subprocess.run(["git", "-C", str(path), "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False)
    repository = Path(root.stdout.strip()) if root.returncode == 0 else path
    scope = str(path.resolve().relative_to(repository.resolve())) if root.returncode == 0 else "."
    status = subprocess.run(
        ["git", "-C", str(repository), "status", "--porcelain", "--", scope],
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "commit": commit.stdout.strip() if commit.returncode == 0 else None,
        "canonical_worktree_clean": status.returncode == 0 and not status.stdout.strip(),
        "canonical_worktree_status": status.stdout.splitlines() if status.returncode == 0 else [],
    }


def write_review_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    source_state = report.get("source_state", {})
    lines = [
        "# Canonical technical-format review",
        "",
        f"Reference locale: `{report['scope']['reference_locale']}`; target locales: "
        f"{', '.join(f'`{locale}`' for locale in report['scope']['target_locales'])}.",
        f"Canonical commit: `{source_state.get('commit')}`; "
        f"canonical worktree clean: `{source_state.get('canonical_worktree_clean')}`.",
        "",
        "This report proposes changes only. It does not modify canonical files. Review the findings CSV and record "
        "decisions in the separate decisions CSV. Format-only proposals are preselected as `apply` for Codex review; "
        "critical token changes remain blank for human validation. Rows requiring structural judgment cannot be applied by the tool.",
        "",
        "## Counts",
        "",
        f"- Compared bodies: {summary['body_pairs_compared']} across {summary['objects_compared']} objects.",
        f"- Exact notation matches: {summary['exact_matches']}.",
        f"- Pairs differing only in translated math labels: {summary['localized_label_only_pairs']} "
        f"({summary['localized_formula_label_count']} formula-label regions kept in their target language).",
        f"- Locale-specific unit-word capitalization cases kept: {summary['localized_unit_word_case_count']}.",
        f"- Findings: {summary['exception_count']}.",
        f"- One-to-one correction proposals: {summary['correction_proposal_count']} "
        f"({summary['format_review_count']} format-only; {summary['critical_proposal_count']} token changes).",
        f"- Cases requiring manual alignment or coverage review: {summary['manual_review_count']}.",
        "",
        "Findings by category:",
        "",
    ]
    for category, count in sorted(summary["exceptions_by_category"].items()):
        lines.append(f"- `{category}`: {count}")
    lines.extend(["", "Findings by target language:", ""])
    for language, values in sorted(summary["exceptions_by_language"].items()):
        details = ", ".join(f"{category}={count}" for category, count in values.items())
        lines.append(f"- `{language}`: {details}")

    samples: list[tuple[str, dict[str, Any]]] = []
    for title, predicate, items in (
        ("Format-only proposal", lambda item: item.get("priority") == "format_review", report["correction_proposals"]),
        ("Critical token proposal", lambda item: item.get("priority") == "critical_human_review", report["correction_proposals"]),
        ("Translated formula label retained", lambda item: item.get("category") == "localized_formula_label", report["localized_label_cases"]),
        ("Localized unit capitalization retained", lambda item: item.get("category") == "localized_unit_word_case", report["localized_label_cases"]),
        ("Structural/manual case", lambda item: item.get("decision") == "manual_review", report["manual_review_cases"]),
    ):
        found = next((item for item in items if predicate(item)), None)
        if found is not None:
            samples.append((title, found))
    lines.extend(["", "## Representative cases", ""])
    for title, item in samples:
        lines.extend(
            [
                f"### {title}: `{item.get('object_path')}` ({item.get('language')})",
                "",
                f"- Finding: `{item.get('finding_category')}`.",
                f"- German: `{item.get('german_text', '')}`",
                f"- Current translation: `{item.get('current_text', '')}`",
                f"- Context (German): {item.get('german_context', '')}",
                f"- Context (target): {item.get('current_context', '')}",
                f"- Recommendation: `{item.get('recommendation', 'manual review')}`.",
                f"- Explanation: {item.get('explanation', 'Requires human review.')}",
                "",
            ]
        )
    lines.extend(
        [
            "## Review files",
            "",
            "- `canonical-technical-format-review.csv`: display-only findings with file hashes and exact fragments.",
            "- `canonical-technical-format-decisions.csv`: editable decision sheet keyed by stable case ID.",
            "- `canonical-technical-format-validation.json`: full technical-region manifest and source snapshot.",
            "",
            "Format-only rows preserve numeric/command tokens and propose German notation. Translated math labels "
            "are recorded separately and preselected `keep`; where their LaTeX wrappers differ, a proposal aligns "
            "the German wrapper while retaining the translated label. The decisions CSV "
            "preselects them for application after the critical cases are reviewed. Token-change rows "
            "propose the aligned German region but require human validation because a value, command or symbol differs. "
            "Order changes, split regions, malformed markup and missing bodies are never auto-paired.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical-root", type=Path, default=REPO.parent / "50ohm-contents-ch" / "canonical")
    parser.add_argument("--locales-config", type=Path, default=REPO / "frontend" / "i18n.config.json")
    parser.add_argument("--manifest", type=Path, default=ORCHESTRATOR / "tmp" / "canonical-technical-format-validation.json")
    parser.add_argument("--review-csv", type=Path, default=ORCHESTRATOR / "tmp" / "canonical-technical-format-review.csv")
    parser.add_argument("--critical-csv", type=Path, default=ORCHESTRATOR / "tmp" / "canonical-technical-format-critical-review.csv")
    parser.add_argument("--decisions-csv", type=Path, default=ORCHESTRATOR / "tmp" / "canonical-technical-format-decisions.csv")
    parser.add_argument("--review-md", type=Path, default=ORCHESTRATOR / "tmp" / "canonical-technical-format-review.md")
    parser.add_argument("--markup-only", action="store_true", help="Propose only source-backed delimiter/markup repairs, preserving technical values")
    args = parser.parse_args()

    config = json.loads(args.locales_config.read_text(encoding="utf-8"))
    default_locale = config["defaultLocale"]
    locales = list(config["locales"])
    if default_locale not in locales or len(set(locales)) != len(locales):
        parser.error("locales config must contain a unique locale list including defaultLocale")

    report = validate(args.canonical_root, default_locale, locales, markup_only=args.markup_only)
    report["source_state"] = _git_snapshot(args.canonical_root.resolve())
    report["source_state"]["locale_config_sha256"] = hashlib.sha256(args.locales_config.read_bytes()).hexdigest()
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_review_csv(report, args.review_csv)
    critical_proposals = [
        item for item in report["correction_proposals"]
        if item.get("priority") == "critical_human_review"
    ]
    write_review_csv(report, args.critical_csv, critical_proposals)
    write_decisions_csv(report, args.decisions_csv)
    write_review_markdown(report, args.review_md)
    print(f"body_pairs_compared={report['summary']['body_pairs_compared']}")
    print(f"exceptions={report['summary']['exception_count']}")
    print(f"correction_proposals={report['summary']['correction_proposal_count']}")
    print(f"manual_review_cases={report['summary']['manual_review_count']}")
    print(f"manifest={args.manifest.resolve()}")
    print(f"review_csv={args.review_csv.resolve()}")
    print(f"critical_csv={args.critical_csv.resolve()}")
    print(f"decisions_csv={args.decisions_csv.resolve()}")
    print(f"review_md={args.review_md.resolve()}")
    if report["summary"]["exception_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
