import re

from mistletoe import span_token
from mistletoe.block_token import BlockToken


class Qso(BlockToken):
    @staticmethod
    def start(line):
        return re.match(r"^\s*<qso>", line)

    @classmethod
    def read(cls, lines):
        child_lines = []

        for line in lines:
            if line.startswith("<qso>"):
                continue
            if line.startswith("</qso>"):
                break
            else:
                child_lines.append(QsoLine(line))
        return child_lines

    def __init__(self, match):
        self.children = match

class QsoLine(BlockToken):
    @classmethod
    def parse_line(cls, line):
        if line.startswith(">"):
            return True, line[1:].strip()
        else:
            return False, line.strip()

    def __init__(self, match):
        self.received, self.text = self.parse_line(match)
        super().__init__(self.text, span_token.tokenize_inner)
