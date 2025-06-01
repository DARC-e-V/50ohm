import re

from mistletoe.span_token import SpanToken


class Include(SpanToken):
    """
    Span token ("[include:ident]").
    Includes raw html or javascript code from a file with the given identifier.
    """

    parse_inner = False
    pattern = re.compile(r'\[include:\s*([^\]]+)\]')
