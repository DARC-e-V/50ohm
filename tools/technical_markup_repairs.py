"""Plan source-backed markup repairs without positional changes to quantities.

Only equivalent formula payloads may acquire the German delimiters. Plain
measurements are paired by value/unit and occurrence, never by their position
among different values. This module performs no filesystem writes.
"""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal, InvalidOperation
import re

try:
    from .technical_format_validation import (
        MEASUREMENT_RE, TOKEN_RE, _code_mask, localized_math_label_relation,
        technical_signature, technical_tokens_equivalent,
    )
except ImportError:
    from technical_format_validation import (
        MEASUREMENT_RE, TOKEN_RE, _code_mask, localized_math_label_relation,
        technical_signature, technical_tokens_equivalent,
    )

GREEK = {"alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "lambda": "λ",
         "omega": "ω", "pi": "π", "rho": "ρ", "phi": "φ", "theta": "θ", "mu": "μ"}
ALIASES = {r"\meter": (r"\meter", r"\metre", r"\m"),
           r"\watt": (r"\watt", r"\W"), r"\dB": (r"\dB", r"\decibel")}
UNITS = {r"\hertz": "Hz", r"\volt": "V", r"\ampere": "A", r"\meter": "m",
         r"\metre": "m", r"\m": "m", r"\watt": "W", r"\W": "W",
         r"\ohm": "Ω", r"\Ohm": "Ω", r"\degree": "°", r"\percent": "%",
         r"\dB": "dB", r"\kilo": "k", r"\milli": "m", r"\mega": "M"}
WORD_UNITS = {"Ampere": "A", "ampère": "A", "ampere": "A", "Volt": "V", "volt": "V",
              "Watt": "W", "watt": "W", "Hertz": "Hz", "hertz": "Hz",
              "Meter": "m", "mètre": "m", "metro": "m"}
LOCAL_WORDS = {"fr": {"Ampere": "ampère", "Volt": "volt", "Watt": "watt", "Hertz": "hertz", "Meter": "mètre"},
               "it": {"Ampere": "ampere", "Volt": "volt", "Watt": "watt", "Hertz": "hertz", "Meter": "metro"}}


def _reference(source_text: str, region: dict, payload: str) -> str:
    return source_text[region["start"]:region["payload_start"]] + payload + source_text[region["payload_end"]:region["end"]]


def _relation(source: str, target: str) -> str | None:
    if technical_tokens_equivalent(TOKEN_RE.findall(source), TOKEN_RE.findall(target)):
        return source
    labels = localized_math_label_relation(source, target)
    if labels:
        return str(labels["proposed_text"])
    # A lost backslash inside an otherwise isolated, delimited Greek symbol.
    if source in {"\\" + name for name in GREEK} and target.strip() == source[1:]:
        return source
    return None


def _scalar(region: dict) -> tuple[str, str] | None:
    text = region["text"].strip()
    if region["kind"] == "measurement":
        match = MEASUREMENT_RE.fullmatch(text)
        if match:
            try:
                return str(Decimal(match["value"].replace(",", "."))), WORD_UNITS.get(match["unit"], match["unit"])
            except InvalidOperation:
                return None  # Ambiguous multi-separator numbers require review.
    match = re.fullmatch(r"\\qty\{([+-]?\d+(?:[.,]\d+)?)\}\{([^{}]+)\}", text)
    if match:
        commands = TOKEN_RE.findall(match[2])
        if commands and all(command in UNITS for command in commands):
            return str(Decimal(match[1].replace(",", "."))), "".join(UNITS[command] for command in commands)
    return None


def _pattern(payload: str) -> re.Pattern:
    parts = []
    for token in TOKEN_RE.findall(payload):
        choices = ALIASES.get(token, (token,))
        if token.startswith("\\") and token[1:] in GREEK:
            choices = (*choices, GREEK[token[1:]])
        if re.fullmatch(r"\d+[.,]\d+", token):
            integer, fractional = re.split(r"[.,]", token)
            part = re.escape(integer) + "[.,]" + re.escape(fractional)
        else:
            part = "(?:" + "|".join(re.escape(choice) for choice in choices) + ")"
        if token.startswith("\\") and token[1:].isalpha():
            part += r"(?![A-Za-z])"
        parts.append(part)
    return re.compile(r"(?<![\w\\])" + r"\s*".join(parts) + r"(?![\w])")


def _has_prose(payload: str) -> bool:
    # Long bare words distinguish a mispaired `$` spanning prose from an
    # enclosing equation. TeX label arguments are allowed to contain prose.
    payload = re.sub(r"\\(?:text|textrm|mathrm)\{[^{}]*\}", "", payload)
    payload = re.sub(r"\\[A-Za-z]+", "", payload)
    words = re.findall(r"\b[a-zA-ZÀ-ÿ]{2,}\b", payload)
    math_words = {"Hz", "kHz", "MHz", "GHz", "dB", "dBm", "dBi", "dBd", "MHz", "Ohm", "mm", "cm", "km", "max", "min", "sin", "cos", "tan", "log", "ln"}
    return any(word not in math_words for word in words)


def _numbers(text: str) -> list[str]:
    result = []
    for match in re.finditer(r"\d+(?:[.,]\d+)*(?:[eE][+-]?\d+)?", text):
        try:
            result.append(str(Decimal(match.group().replace(",", ".")).normalize()))
        except InvalidOperation:
            result.append(match.group())
    return result


def plan_markup_repairs(source_text: str, target_text: str, locale: str) -> tuple[str, list[dict]]:
    source = technical_signature(source_text)
    references = [(index, region) for index, region in enumerate(source["regions"])
                  if region["kind"] in {"math", "html_math"}
                  and not any(region["start"] <= issue["offset"] < region["end"] for issue in source["syntax_findings"])]
    source_scalars = defaultdict(list)
    for index, region in enumerate(source["regions"]):
        key = _scalar(region)
        if key:
            source_scalars[key].append((index, region))
    updated = target_text
    history: list[dict] = []

    def apply(patches: list[tuple[int, int, str, int, str]]) -> None:
        nonlocal updated
        selected = []
        for patch in sorted(patches, key=lambda item: (-(item[1] - item[0]), item[0])):
            if not any(patch[0] < other[1] and other[0] < patch[1] for other in selected):
                selected.append(patch)
        for start, end, replacement, reference_index, reason in sorted(selected, reverse=True):
            if updated[start:end] == replacement:
                continue
            if _numbers(updated[start:end]) != _numbers(replacement):
                raise ValueError("A markup-only repair must preserve the ordered numeric values")
            history.append({"start": start, "end": end, "expected": updated[start:end], "replacement": replacement,
                            "reference_region_index": reference_index,
                            "reference_text": source["regions"][reference_index]["text"], "reason": reason})
            updated = updated[:start] + replacement + updated[end:]

    for _ in range(6):
        before = updated
        target = technical_signature(updated)
        patches = []
        target_scalars = defaultdict(list)
        for region in target["regions"]:
            key = _scalar(region)
            if key:
                target_scalars[key].append(region)
        plain_replacements = {}
        for key, originals in source_scalars.items():
            translations = target_scalars.get(key, [])
            if len(originals) != len(translations):
                continue
            for (index, original), translation in zip(originals, translations, strict=True):
                if original["kind"] == "measurement" and translation["kind"] in {"math", "html_math"}:
                    value = original["text"]
                    for word, localized in LOCAL_WORDS.get(locale, {}).items():
                        value = value.replace(word, localized)
                    plain_replacements[translation["start"]] = (value, index)
        for region in target["regions"]:
            if region["kind"] not in {"math", "html_math"}:
                continue
            if region["start"] in plain_replacements:
                replacement, index = plain_replacements[region["start"]]
                patches.append((region["start"], region["end"], replacement, index, "German reference is a plain measurement"))
                continue
            matches = []
            for index, original in references:
                payload = _relation(original["text"], region["text"])
                if payload is not None:
                    matches.append((_reference(source_text, original, payload), index))
            if matches and len({value for value, _ in matches}) == 1:
                replacement, index = matches[0]
                patches.append((region["start"], region["end"], replacement, index, "Equivalent payload; use German math markup"))
        apply(patches)

        target = technical_signature(updated)
        masked = _code_mask(updated)
        masked = re.sub(r"<[^>]+>", lambda match: " " * len(match.group()), masked)
        protected = [region for region in target["regions"] if region["kind"] in {"math", "html_math"} and not _has_prose(region["text"])]
        patches = []
        by_payload = defaultdict(list)
        for index, region in references:
            by_payload[region["text"]].append((index, region))
        for payload, originals in sorted(by_payload.items(), key=lambda item: -len(item[0])):
            if not ("\\" in payload or "=" in payload or "/" in payload):
                continue  # Never wrap ordinary prose numbers or variable letters.
            index, original = originals[0]
            if len({_reference(source_text, region, payload) for _, region in originals}) != 1:
                continue
            candidates = []
            for match in _pattern(payload).finditer(masked):
                if any(region["start"] <= match.start() and match.end() <= region["end"] for region in protected):
                    continue
                # Inside a malformed span, only repair a source-backed payload
                # at its opening; never wrap a subexpression inside an equation.
                enclosing = [region for region in target["regions"] if region["kind"] in {"math", "html_math"} and region["start"] <= match.start() < region["end"]]
                if enclosing and not any(region["payload_start"] == match.start() for region in enclosing):
                    continue
                candidates.append(match)
            used = sum(1 for region in target["regions"] if region["kind"] in {"math", "html_math"} and _relation(payload, region["text"]) is not None)
            if used + len(candidates) > len(originals):
                continue  # Extra occurrences require review, not added formula markup.
            for match in candidates:
                start, end = match.span()
                if start and updated[start - 1] == "$" and not (start > 1 and updated[start - 2] == "$"):
                    start -= 1
                if end < len(updated) and updated[end] == "$" and not (end + 1 < len(updated) and updated[end + 1] == "$"):
                    end += 1
                replacement = _reference(source_text, original, payload)
                patches.append((start, end, replacement, index, "Restore missing German math delimiters around an equivalent payload"))
        apply(patches)
        if updated == before:
            break
    return updated, history
