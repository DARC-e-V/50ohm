import re

from mistletoe.block_token import BlockToken


class Include(BlockToken):
    """
    Block token ("[include:ident]").
    Includes raw html or javascript code from a file with the given identifier.
    """

    pattern = re.compile(r"^\s*\[include:\s*([^\]]+)\]", re.MULTILINE)

    @classmethod
    def start(cls, line):
        return cls.pattern.match(line)

    @classmethod
    def read(cls, lines):
        line = next(lines)  # Consume the line with the include directive
        return cls.pattern.match(line).group(1)

    def __init__(self, match):
        self.ident = match
