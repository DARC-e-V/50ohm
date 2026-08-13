import re

from mistletoe.block_token import BlockToken


class Question(BlockToken):
    pattern = re.compile(r"^\s*\[question:([\w\d]+)\]", re.MULTILINE)

    @classmethod
    def start(cls, line):
        return cls.pattern.match(line)

    @classmethod
    def read(cls, lines):
        first_line = next(lines)
        return cls.pattern.match(first_line).group(1)

    @classmethod
    def check_interrupts_paragraph(cls, lines):
        return cls.start(lines.peek())

    def __init__(self, match):
        self.question_number = match
