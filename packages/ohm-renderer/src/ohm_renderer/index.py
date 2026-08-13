import re

from mistletoe.span_token import SpanToken


class Index(SpanToken):
    """
    Resolve index commands
    Identifies "[index:term:subterm]" or "[index:term]"
    """

    pattern = re.compile(r"[ \t]*\[index:([^:\]\s](?:[^:\]\s]| )*)(?::([^:\]\s](?:[^:\]\s]| )*))?\]")

    def __init__(self, match_object):
        self.first = match_object.group(1)
        self.second = match_object.group(2)


def normalize_index_part(value: str) -> str:
    """Reduces a term to the characters that are safe inside an anchor id."""
    normalized = value.strip().lower()
    normalized = re.sub(r"\s+", "_", normalized)
    normalized = re.sub(r"[^\w]", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or "index"


def index_anchor_id(first: str, second: str | None = None) -> str:
    """The anchor id an index entry gets, shared by the renderers and the builders."""
    normalized = normalize_index_part(first)
    if second:
        return f"index_{normalized}__{normalize_index_part(second)}"
    return f"index_{normalized}"
