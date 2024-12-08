import re

from mistletoe.span_token import SpanToken


class Dash(SpanToken):
    """
    Dash span token ( - ).
    Identifies a dash in a text.
    """
    pattern = re.compile(r'(\s-\s)')
