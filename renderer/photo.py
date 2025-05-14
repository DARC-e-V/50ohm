import re

from mistletoe.span_token import SpanToken


class Photo(SpanToken):
    """
    Span token for photos.
    Example: [photo:123:n_wasserfalldiagramm_trx_collage:Ansichten verschiedener Transceiver]
    """

    parse_inner = False
    pattern = re.compile(r"\[photo:(\d+):([^:\]]+):([^:\]]+)\]")

    def __init__(self, match_object):
        self.id = match_object.group(1)
        self.ref = match_object.group(2)
        self.text = match_object.group(3)
        self.number = "TODO"