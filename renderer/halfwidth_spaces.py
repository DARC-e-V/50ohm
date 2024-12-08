import re

from mistletoe.span_token import SpanToken


class HalfwidthSpaces(SpanToken):
    """
    Insert halfwidth space into span token (Z. B.)
    Identifies "z.B.", "d.h." and "D.h." with and without space in between.
    """
    pattern = re.compile(r"\b(z|d|D)\.(B|h)\.")

    def __init__(self, match_object):
        self.first = match_object.group(1)
        self.second = match_object.group(2)



