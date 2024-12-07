from mistletoe import HtmlRenderer
from mistletoe.block_token import BlockToken


class FiftyOhmHtmlRenderer(HtmlRenderer):
    def __init__(self):
        super().__init__(Comment)

    def render_comment():
        return None


class Comment(BlockToken):
    @staticmethod
    def start(line):
        return line.startswith("%")

    @classmethod
    def read(cls, lines):
        next(lines)
        return None
