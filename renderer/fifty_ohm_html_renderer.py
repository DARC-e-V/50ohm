from mistletoe import HtmlRenderer

from .comment import Comment
from .unit import Unit
from .quote import Quote


units = {
    "A": "A",
    "Ah": "Ah",
    "A/mm²": "A/mm²",
    "baud": "baud",
    "Bit": "Bit",
    "Bit/s": "Bit/s",
    "dB": "dB",
    "dBi": "dBi",
    "dBm": "dBm",
    "dBW": "dBW",
    "F": "F",
    "J": "J",
    "Hz": "Hz",
    "H": "H",
    "cm": "cm",
    "m": "m",
    "m²": "m²",
    "Ohm": "Ω",
    "ppm": "ppm",
    "pps": "pps",
    "s": "s",
    "V": "V",
    "W": "W",
    "Wh": "Wh",
    "°": "°",
    "%": "%",
}

no_space_units = ["°", "%"]


class FiftyOhmHtmlRenderer(HtmlRenderer):
    def __init__(self):
        super().__init__(Comment, Unit, Quote)

    def render_comment():
        return None

    def render_quote(self, token):
        return f"„{self.render_inner(token)}“"

    def render_underline(self, token):
        return f"<u>{self.render_inner(token)}</u>"

    @staticmethod
    def render_unit(token):
        unit = token.prefix + units[token.unit]
        if token.unit in no_space_units:
            return f"{token.value}{unit}"
        else:
            return f"{token.value}&#8239;{unit}"
