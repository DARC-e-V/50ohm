import re

from mistletoe.span_token import SpanToken


class Smartquote(SpanToken):
    """
    Smart quote span token ("Eiersalat").
    Identifies quoted text.
    """

    pattern = re.compile(r'"([^"]+)"')
