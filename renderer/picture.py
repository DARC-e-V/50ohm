import re

from mistletoe.span_token import SpanToken


class Picture(SpanToken):
    """
    Span token for pictures.
    Example: [picture:727:amplitude_periode_halbwellen:Positive und negative Halbwellen einer Sinusschwingung]
    """

    parse_inner = False
    pattern = re.compile(r"\[picture:(\d+):(.+):(.+)\]")

    def __init__(self, match_object):
        self.id = match_object.group(1)
        self.ref = match_object.group(2)
        self.text = match_object.group(3)
