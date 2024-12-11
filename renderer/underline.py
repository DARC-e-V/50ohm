import re

from mistletoe.span_token import SpanToken


class Underline(SpanToken):
    """
    Underline span token (<u>Untersrich</u>).
    Identifies underlined text.
    """

    pattern = re.compile(r"<u>(.+)</u>")
