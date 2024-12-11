import re

from mistletoe.span_token import SpanToken


class Quote(SpanToken):
    """
    Quote span token ("Eiersalat").
    Identifies quoted text.
    """

    pattern = re.compile(r'"([^"]+)"')
