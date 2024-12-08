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
        r"([0-9,]+) ?("
        # Group all prefixes together in a capture group
        # Empty string at end of list is required so the group always exists in the resulting match
        + "|".join(prefixes + [""])
        + ")("
        # Group all units together in a capture group.
        + "|".join(units)
        + r")(?!\w)"
    )

    def __init__(self, match):
        self.value = match.group(1)
        self.prefix = match.group(2)
        self.unit = match.group(3)
