"""Deterministic comparison of technical notation in canonical content bodies."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path


TOKEN_RE = re.compile(r"\\[A-Za-z]+[*]?|\d+(?:[.,]\d+)*(?:[eE][+-]?\d+)?|[A-Za-z]+|[^\s]")
COMMAND_RE = re.compile(r"\\[A-Za-z]+[*]?")
HTML_MATH_RE = re.compile(
    r"\\?<span\b(?=[^>]*\bclass\s*=\s*(['\"])[^'\"]*\bmath\b[^'\"]*\1)[^>]*>(.*?)</span\s*>",
    re.IGNORECASE | re.DOTALL,
)
HTML_MATH_START_RE = re.compile(r"\\?<span\b(?=[^>]*\bclass\s*=\s*['\"][^'\"]*\bmath\b)", re.I)
MEASUREMENT_RE = re.compile(
    r"(?<![\w])(?P<value>[+-]?\d+(?:[.,]\d+)*(?:[eE][+-]?\d+)?)"
    r"[ \u00a0]*(?P<unit>Ampere|ampère|ampere|Volt|volt|Watt|watt|Hertz|hertz|Meter|mètre|metro|"
    r"%|‰|°|(?:[fpnumkMGTµμ]?)(?:Hz|V|A|W|Ohm|Ω|F|H|s|m|km|cm|mm|bit|Bit|baud)|dB(?:m|i|d)?)(?![\w])"
)
BODY_RE = re.compile(r"^body\.(?P<language>[a-z]{2})\.(?P<extension>md|html)$")
DECIMAL_TOKEN_RE = re.compile(r"^[+-]?\d+[.,]\d+$")
MATH_LABEL_RE = re.compile(r"\\(?P<command>text|textrm|mathrm)\{(?P<label>[^{}]*)\}")
FIXED_MATH_LABELS = {
    "A", "V", "W", "Hz", "Ohm", "Ω", "F", "H", "s", "m", "km", "cm", "mm",
    "bit", "bits", "dB", "dBm", "dBi", "dBd", "eff", "max", "min", "RMS", "rms",
}


@dataclass(frozen=True)
class Region:
    kind: str
    delimiter: str
    text: str
    start: int
    end: int
    payload_start: int
    payload_end: int

    @property
    def tokens(self) -> list[str]:
        return TOKEN_RE.findall(self.text)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _code_mask(text: str) -> str:
    """Blank code and embedded scripts so examples aren't treated as course notation."""
    chars = list(text)
    ignored_spans = [
        *re.finditer(r"(?ms)^\s*```.*?^\s*```[^\n]*(?:\n|$)", text),
        *re.finditer(r"(?is)<(script|style)\b[^>]*>.*?</\1\s*>", text),
    ]
    for match in ignored_spans:
        for index in range(match.start(), match.end()):
            if chars[index] != "\n":
                chars[index] = " "
    masked = "".join(chars)
    chars = list(masked)
    for match in re.finditer(r"(?<!\\)`+.*?(?<!\\)`+", masked):
        for index in range(match.start(), match.end()):
            if chars[index] != "\n":
                chars[index] = " "
    return "".join(chars)


def _matching_delimiter(text: str, start: int, delimiter: str) -> int | None:
    index = start
    while index < len(text):
        if text.startswith(delimiter, index) and (index == 0 or text[index - 1] != "\\"):
            return index
        index += 1
    return None


def _matching_brace(text: str, start: int) -> int | None:
    if start >= len(text) or text[start] != "{":
        return None
    depth = 0
    index = start
    while index < len(text):
        if text[index] == "\\":
            index += 2
            continue
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def _brace_findings(text: str, offset: int) -> list[dict[str, object]]:
    stack: list[int] = []
    findings = []
    index = 0
    while index < len(text):
        if text[index] == "\\":
            index += 2
            continue
        if text[index] == "%":
            newline = text.find("\n", index)
            index = len(text) if newline < 0 else newline + 1
            continue
        if text[index] == "{":
            stack.append(index)
        elif text[index] == "}":
            if stack:
                stack.pop()
            else:
                findings.append({"code": "unmatched_math_brace", "offset": offset + index})
        index += 1
    findings.extend({"code": "unmatched_math_brace", "offset": offset + value} for value in stack)
    return findings


def extract_regions(text: str) -> tuple[list[Region], list[dict[str, object]]]:
    """Extract math and raw TeX/physical-measurement regions, plus syntax findings."""
    masked = _code_mask(text)
    regions: list[Region] = []
    findings: list[dict[str, object]] = []
    occupied: list[tuple[int, int]] = []

    for match in HTML_MATH_RE.finditer(masked):
        body = match.group(2)
        findings.extend(_brace_findings(body, match.start(2)))
        regions.append(Region("html_math", "span", body, match.start(), match.end(), match.start(2), match.end(2)))
        occupied.append((match.start(), match.end()))
    for match in HTML_MATH_START_RE.finditer(masked):
        if not any(start <= match.start() < end for start, end in occupied):
            findings.append({"code": "unclosed_html_math_span", "offset": match.start()})

    for start, end in occupied:
        masked = masked[:start] + ("\n" * masked[start:end].count("\n")) + (" " * (end - start - masked[start:end].count("\n"))) + masked[end:]

    index = 0
    while index < len(masked):
        delimiter = None
        content_start = index
        if masked.startswith("$$", index):
            delimiter, content_start = "$$", index + 2
        elif masked.startswith(r"\(", index):
            delimiter, content_start = r"\(", index + 2
        elif masked.startswith(r"\[", index):
            delimiter, content_start = r"\[", index + 2
        elif masked[index] == "$" and (index == 0 or masked[index - 1] != "\\"):
            delimiter, content_start = "$", index + 1
        if delimiter is None:
            index += 1
            continue
        closing = {"$$": "$$", "$": "$", r"\(": r"\)", r"\[": r"\]"}[delimiter]
        end = _matching_delimiter(masked, content_start, closing)
        if end is None:
            findings.append({"code": "unmatched_math_delimiter", "delimiter": delimiter, "offset": index})
            regions.append(Region("math", delimiter, text[content_start:], index, len(text), content_start, len(text)))
            break
        inner_text = text[content_start:end]
        findings.extend(_brace_findings(inner_text, content_start))
        nested = re.search(r"(?<!\\)(?:\$|\\\(|\\\[|\\\)|\\\])", inner_text)
        if nested:
            findings.append(
                {
                    "code": "nested_math_delimiter",
                    "delimiter": delimiter,
                    "nested_delimiter": nested.group(),
                    "offset": content_start + nested.start(),
                }
            )
        regions.append(Region("math", delimiter, inner_text, index, end + len(closing), content_start, end))
        index = end + len(closing)

    # Only inspect commands outside math spans. A command plus all immediately
    # following brace groups is one technical atom (for example \qty{...}{...}).
    occupied_math = [(region.start, region.end) for region in regions]
    for match in COMMAND_RE.finditer(masked):
        if any(start <= match.start() < end for start, end in occupied_math):
            continue
        end = match.end()
        argument = end
        while argument < len(masked) and masked[argument].isspace():
            argument += 1
        while argument < len(masked) and masked[argument] == "{":
            brace_end = _matching_brace(masked, argument)
            if brace_end is None:
                findings.append({"code": "unmatched_tex_argument", "command": match.group(), "offset": match.start()})
                break
            end = argument = brace_end + 1
        regions.append(Region("raw_tex", "command", text[match.start():end], match.start(), end, match.start(), end))

    for match in MEASUREMENT_RE.finditer(masked):
        if any(start <= match.start() < end for start, end in occupied_math):
            continue
        regions.append(
            Region("measurement", "unit_text", match.group(), match.start(), match.end(), match.start(), match.end())
        )

    regions.sort(key=lambda region: (region.start, region.end, region.kind))
    # Avoid overlapping raw TeX/measurement regions; retain the earlier, broader atom.
    non_overlapping: list[Region] = []
    for region in regions:
        if non_overlapping and region.start < non_overlapping[-1].end:
            continue
        non_overlapping.append(region)
    return non_overlapping, findings


def technical_signature(text: str) -> dict[str, object]:
    regions, findings = extract_regions(text)
    token_stream = [token for region in regions for token in region.tokens]
    structure = [
        {
            "kind": region.kind,
            "delimiter": region.delimiter,
            "start": region.start,
            "end": region.end,
            "payload_start": region.payload_start,
            "payload_end": region.payload_end,
            "text": region.text,
            "tokens": region.tokens,
        }
        for region in regions
    ]
    return {
        "sha256": sha256_text(text),
        "technical_tokens": token_stream,
        "token_counts": dict(sorted(Counter(token_stream).items())),
        "regions": structure,
        "syntax_findings": findings,
    }


def _token_group(tokens: list[str], start: int) -> tuple[list[str], int] | None:
    if start >= len(tokens) or tokens[start] != "{":
        return None
    depth = 0
    for index in range(start, len(tokens)):
        if tokens[index] == "{":
            depth += 1
        elif tokens[index] == "}":
            depth -= 1
            if depth == 0:
                return tokens[start + 1 : index], index + 1
    return None


def _is_single_math_atom(tokens: list[str]) -> bool:
    if len(tokens) == 1:
        return True
    if len(tokens) >= 2 and tokens[0].startswith("\\"):
        # A command followed only by complete braced arguments is one atom,
        # e.g. \sqrt{2} or \qty{50}{\ohm}.
        index = 1
        while index < len(tokens):
            group = _token_group(tokens, index)
            if group is None:
                return False
            _, index = group
        return index == len(tokens)
    return False


def _normalize_fraction_notation(tokens: list[str]) -> list[str]:
    """Normalize simple TeX fraction wrappers to an equivalent slash form.

    This is deliberately syntactic: it handles explicit \\frac/\\dfrac/\\tfrac
    forms, without attempting algebraic simplification or changing values.
    """
    result: list[str] = []
    index = 0
    while index < len(tokens):
        if tokens[index] in {"\\frac", "\\dfrac", "\\tfrac"}:
            numerator = _token_group(tokens, index + 1)
            if numerator is not None:
                denominator = _token_group(tokens, numerator[1])
                if denominator is not None:
                    left = _normalize_fraction_notation(numerator[0])
                    right = _normalize_fraction_notation(denominator[0])
                    result.extend(left if _is_single_math_atom(left) else ["(", *left, ")"])
                    result.append("/")
                    result.extend(right if _is_single_math_atom(right) else ["(", *right, ")"])
                    index = denominator[1]
                    continue
        result.append(tokens[index])
        index += 1
    return result


def _normalize_equivalent_tokens(tokens: list[str]) -> list[str]:
    aliases = {
        "\\dfrac": "\\frac",
        "\\tfrac": "\\frac",
        "\\metre": "\\meter",
        "\\m": "\\meter",
        "\\W": "\\watt",
        "\\decibel": "\\dB",
        "\\Ohm": "\\ohm",
        "\\Omega": "\\ohm",
    }
    normalized = [aliases.get(token, token) for token in tokens]
    return _normalize_fraction_notation(normalized)


def technical_tokens_equivalent(source: list[str], target: list[str]) -> bool:
    # Proven notation aliases and equivalent fraction syntax are format
    # differences. The correction workflow then proposes the exact German
    # region and preselects it for application.
    source = _normalize_equivalent_tokens(source)
    target = _normalize_equivalent_tokens(target)
    if len(source) != len(target):
        return False
    for index, (source_token, target_token) in enumerate(zip(source, target, strict=True)):
        if source_token == target_token:
            continue
        # "bit" is a translated unit word in German technical prose; its
        # capitalization follows the sentence language, unlike SI symbols.
        if (
            source_token.lower() == target_token.lower() == "bit"
            and index > 0
            and re.fullmatch(r"[+-]?\d+(?:[.,]\d+)*", source[index - 1])
            and source[index - 1] == target[index - 1]
        ):
            continue
        if not DECIMAL_TOKEN_RE.fullmatch(source_token) or not DECIMAL_TOKEN_RE.fullmatch(target_token):
            return False
        try:
            if Decimal(source_token.replace(",", ".")) != Decimal(target_token.replace(",", ".")):
                return False
        except InvalidOperation:
            return False
    return True


def localized_math_label_relation(source: str, target: str) -> dict[str, object] | None:
    """Return a safe text-label alignment when only translatable math labels differ."""
    source_matches = list(MATH_LABEL_RE.finditer(source))
    target_matches = list(MATH_LABEL_RE.finditer(target))
    if not source_matches or len(source_matches) != len(target_matches):
        return None

    def skeleton(text: str) -> str:
        return MATH_LABEL_RE.sub(r"\\MATHLABEL{}", text)

    if skeleton(source) != skeleton(target):
        return None
    changed_labels = []
    command_style_differs = False
    for source_match, target_match in zip(source_matches, target_matches, strict=True):
        source_label = source_match.group("label")
        target_label = target_match.group("label")
        if source_label == target_label:
            command_style_differs |= source_match.group("command") != target_match.group("command")
            continue
        if re.findall(r"\d+", source_label) != re.findall(r"\d+", target_label):
            return None
        if len(source_label.strip()) == len(target_label.strip()) == 1:
            return None
        if source_label in FIXED_MATH_LABELS or target_label in FIXED_MATH_LABELS:
            return None
        if not re.fullmatch(r"[\wÀ-ÿ .-]+", source_label, flags=re.UNICODE) or not re.fullmatch(
            r"[\wÀ-ÿ .-]+", target_label, flags=re.UNICODE
        ):
            return None
        changed_labels.append({"source": source_label, "target": target_label})
        command_style_differs |= source_match.group("command") != target_match.group("command")
    if not changed_labels:
        return None

    # Keep translated label text, while adopting the exact German math wrapper.
    replacement = source
    for source_match, target_match in reversed(list(zip(source_matches, target_matches, strict=True))):
        replacement = (
            replacement[: source_match.start()]
            + f"\\{source_match.group('command')}{{{target_match.group('label')}}}"
            + replacement[source_match.end() :]
        )
    return {
        "labels": changed_labels,
        "command_style_differs": command_style_differs,
        "proposed_text": replacement,
    }


def same_measurement_with_bit_capitalization(source: str, target: str) -> bool:
    pattern = re.compile(r"^(?P<value>[+-]?\d+(?:[.,]\d+)*)\s*(?P<unit>bit|Bit)$")
    source_match = pattern.fullmatch(source)
    target_match = pattern.fullmatch(target)
    return bool(
        source_match
        and target_match
        and source_match.group("value") == target_match.group("value")
        and source_match.group("unit").lower() == target_match.group("unit").lower()
    )


def classify_pair(source: dict[str, object], target: dict[str, object]) -> str:
    if source["syntax_findings"] or target["syntax_findings"]:
        return "malformed_technical_markup"
    source_tokens = source["technical_tokens"]
    target_tokens = target["technical_tokens"]
    source_regions = source["regions"]
    target_regions = target["regions"]
    if technical_tokens_equivalent(source_tokens, target_tokens):
        same_boundaries = len(source_regions) == len(target_regions) and all(
            (source_region["kind"], source_region["delimiter"])
            == (target_region["kind"], target_region["delimiter"])
            for source_region, target_region in zip(source_regions, target_regions, strict=True)
        )
        if not same_boundaries:
            return "same_technical_tokens_different_boundaries"
        if any(source_region["text"] != target_region["text"] for source_region, target_region in zip(source_regions, target_regions, strict=True)):
            return "technical_format_mismatch"
        return "match"
    if (
        len(source_regions) == len(target_regions)
        and all(
            (left["kind"], left["delimiter"]) == (right["kind"], right["delimiter"])
            for left, right in zip(source_regions, target_regions, strict=True)
        )
        and all(
            left["text"] == right["text"] or localized_math_label_relation(left["text"], right["text"])
            for left, right in zip(source_regions, target_regions, strict=True)
        )
    ):
        if any(
            left["text"] != right["text"]
            and not localized_math_label_relation(left["text"], right["text"])["command_style_differs"]
            for left, right in zip(source_regions, target_regions, strict=True)
        ):
            return "localized_formula_label"
        return "localized_label_markup_mismatch"
    if Counter(_normalize_equivalent_tokens(source_tokens)) == Counter(_normalize_equivalent_tokens(target_tokens)):
        return "same_technical_tokens_different_order"
    return "technical_token_mismatch"


def body_inventory(canonical_root: Path) -> dict[tuple[str, str], dict[str, Path]]:
    inventory: dict[tuple[str, str], dict[str, Path]] = {}
    for path in sorted(canonical_root.rglob("body.*.*")):
        match = BODY_RE.match(path.name)
        if not match:
            continue
        object_path = path.parent.relative_to(canonical_root).as_posix()
        suffix = match.group("extension")
        inventory.setdefault((object_path, suffix), {})[match.group("language")] = path
    return inventory
