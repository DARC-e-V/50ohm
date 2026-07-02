import re

from mistletoe.block_token import BlockToken


class Include(BlockToken):
    """
    Block token ("[include:ident]").
    Includes raw html or javascript code from a file with the given identifier.
    """

    @staticmethod
    def start(line):
        return re.match(r"^\s*\[include:\s*[^\]]+\]", line)

    @classmethod
    def read(cls, lines):
        re.compile(r"")
        line = next(lines)  # Consume the line with the include directive
        ident = re.match(r"^\s*\[include:\s*([^\]]+)\]", line).group(1)
        return ident

    def __init__(self, match):
        self.ident = match
