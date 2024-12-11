import re

from mistletoe.block_token import BlockToken
from mistletoe.span_token import SpanToken


class SpanComment(SpanToken):
    """
    Coment span token (% Eiersalat).
    Identifies a comment in text.
    """

    pattern = re.compile(r"(%.*\n?)")


class BlockComment(BlockToken):
    @staticmethod
    def start(line):
        return line.startswith("%")

    @classmethod
    def read(cls, lines):
        next(lines)
        return None
