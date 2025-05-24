import re

from mistletoe.span_token import SpanToken


class Unit(SpanToken):
    units = [
        "A",
        "Ah",
        "A/mm²",
        "baud",
        "Bit",
        "Bit/s",
        "dB",
        "dBi",
        "dBm",
        "dBW",
        "F",
        "J",
        "Hz",
        "H",
        "cm",
        "m",
        "m²",
        "Ohm",
        "ppm",
        "pps",
        "s",
        "V",
        "W",
        "Wh",
        "°",
        "%",
    ]
    prefixes = ["p", "n", "μ", "m", "k", "M", "G"]

    pattern = re.compile(
        # Check for word boundary at start of value ensures only numeric values are caught.
        r"\b(?P<value>[0-9,]+) ?(?P<prefix>"
        # Group all prefixes together in a capture group
        # Empty string at end of list is required so the group always exists in the resulting match
        + "|".join(prefixes + [""])
        + ")(?P<unit>"
        # Group all units together in a capture group.
        + "|".join(units)
        # Word boundary check at end of unit to ensure proper handling of units like A, Ah etc.
        + r")\b"
    )

    value: str
    prefix: str
    unit: str

    def __init__(self, match: re.Match):
        print("pattern", self.pattern)

        self.value = match.group("value")
        self.prefix = match.group("prefix") or ""
        self.unit = match.group("unit")
