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
        r"(?P<value>[0-9,]+) ?(?P<prefix>"
        # Group all prefixes together in a capture group
        # Empty string at end of list is required so the group always exists in the resulting match
        + "|".join(prefixes + [""])
        + ")(?P<unit>"
        # Group all units together in a capture group.
        + "|".join(units)
        + r")(?!\w)"
    )

    value: str
    prefix: str
    unit: str

    def __init__(self, match: re.Match):
        self.value = match.group("value")
        self.prefix = match.group("prefix") or ""
        self.unit = match.group("unit")
