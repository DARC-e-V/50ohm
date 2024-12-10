import re

from mistletoe.span_token import SpanToken


class NonbreakingSpaces(SpanToken):
    """
    Insert unbreakable space into span token (§ 3)
    Identifies "§$number", "Abs.$number", "Klasse [A,E,N]" w/ and without space between.
    """
    pattern = re.compile(r"(§|Abs\.|Klasse)\s?(\d|[NEA])")

    def __init__(self, match_object):
        self.first = match_object.group(1)
        self.second = match_object.group(2)

class NonbreakingSpacesDots(SpanToken):
    """
    Insert unbreakable space before and after "..." if there is a space
    Identifies "..." with leading and/or trailing space
    """
    pattern = re.compile(r"(\s?)(\.\.\.)(\s?)")

    def __init__(self, match_object):
        self.first = match_object.group(1)
        self.second = match_object.group(2)
        self.third = match_object.group(3)
        


