import re

from mistletoe.span_token import SpanToken


class Reference(SpanToken):
    """
    Resolve references for html
    Identifies "[ref:$]"
    """

    pattern = re.compile(r"\[ref\:(\S+)\]")

    def __init__(self, match_object):
        self.marker: str = match_object.group(1)
