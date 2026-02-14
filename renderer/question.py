import re

from mistletoe.block_token import BlockToken


class Question(BlockToken):
    @staticmethod
    def start(line):
        # Search for:
        # [question:123]
        return re.match(r"^\s*\[question:[\w\d]+\]", line)

    @classmethod
    def read(cls, lines):
        first_line = next(lines)
        question_number = re.match(r"^\s*\[question:([\w\d]+)\]", first_line).group(1)
        return question_number

    @classmethod
    def check_interrupts_paragraph(cls, lines):
        return cls.start(lines.peek())

    def __init__(self, match):
        self.question_number = match
