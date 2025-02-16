import re

from mistletoe.block_token import BlockToken
from mistletoe.span_token import SpanToken

# class SpanComment(SpanToken):
#     """
#     Coment span token (% Eiersalat).
#     Identifies a comment in text.
#     """
#
#     pattern = re.compile(r"(%.*\n?)")


class BlockComment(BlockToken):
    def __init__(self, match):
        self.content = match
        self.children = []

    @staticmethod
    def start(line):
        return line.startswith("%")

    @classmethod
    def check_interrupts_paragraph(cls, lines):
        return cls.start(lines.peek())

    @classmethod
    def read(cls, lines):
        comment = re.match(r"%(.*)", next(lines)).group(1).strip()
        return comment
