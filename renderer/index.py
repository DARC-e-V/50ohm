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
