
# ^\s*---\s*(.*)\s*$
import re

from mistletoe.block_token import BlockToken, tokenize


class SlideBreak(BlockToken):
    @staticmethod
    def start(line):
        return re.match(r"^\s*---.*$", line)

    @classmethod
    def read(cls, lines):
        child_lines = []
        first_line = next(lines) # Consume the line that started the slide break

        match = re.match(r"^\s*---\s*(.*)\s*.*$", first_line)
        attribute = match.group(1) if match.group(1) else None

        # We have to work with peak here, since a normal for loop would already
        # consume the next line, which might be a `---` line that marks the
        # beginning of a new slide as well
        next_line = lines.peek()
        while next_line is not None:
            if re.match(r"^\s*---.*$", next_line) :
                break 
            else:
                child_lines.append(next(lines))
                next_line = lines.peek()

        return tokenize(child_lines), attribute

    def __init__(self, match):
        self.children, self.attribute = match
