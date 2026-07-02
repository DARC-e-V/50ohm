import re

from mistletoe.block_token import BlockToken


class Formula(BlockToken):
    r"""
    Block token ("$ a \cdot b $").
    Transfroms a line that contains only a formula enclosed in dollar signs into a Formula token.
    """

    @staticmethod
    def start(line):
        return re.match(r"^\s*\$[^$]+\$\s*$", line)

    @classmethod
    def check_interrupts_paragraph(cls, lines):
        return cls.start(lines.peek())

    @classmethod
    def read(cls, lines):
        line = next(lines)  # Consume the line with the formula
        formula = re.match(r"^\s*\$([^$]+)\$\s*$", line).group(1)
        return formula

    def __init__(self, match):
        self.formula = match
