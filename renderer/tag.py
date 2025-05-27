import re

from mistletoe.block_token import BlockToken, tokenize

captures = [
    "margin",
    "indepth",
    "webmargin",
    "warning",
    "attention",
    "tip",
    "webtip",
    "webindepth",
    "person",
    "fullwidth",
    "unit",
    "danger",
    "webonly",
    "latexonly",
    "wordorigin",
]


class Tag(BlockToken):
    @staticmethod
    def start(line):
        return re.match(r"^\s*<(" + "|".join(captures) + r")+>", line)

    @classmethod
    def read(cls, lines):
        child_lines = []
        first_line = next(lines)

        tagtype = re.match(r"^\s*<([^>]+)>", first_line).group(1)

        for line in lines:
            if line.startswith(f"</{tagtype}>"):
                break
            else:
                child_lines.append(line)
        return tagtype, tokenize(child_lines)

    def __init__(self, match):
        self.tagtype, self.children = match
