import re

from mistletoe.block_tokenizer import FileWrapper

from renderer.referenced_token import ReferencedToken


class Picture(ReferencedToken):
    """
    Span token for pictures.
    Example: [picture:727:amplitude_periode_halbwellen:Positive und negative Halbwellen einer Sinusschwingung]
    """

    pattern = re.compile(r"^\[picture:(?P<id>\d+):(?P<marker>[^:\]]+):(?P<text>[^:\]]+)\]$")

    @classmethod
    def start(cls, line: str):
        return cls.pattern.match(line.strip()) is not None

    @classmethod
    def check_interrupts_paragraph(cls, lines: FileWrapper):
        return cls.pattern.match(lines.peek())

    @classmethod
    def read(cls, lines: FileWrapper):
        match = cls.pattern.match(next(lines))
        return match.group("id"), match.group("marker"), match.group("text")

    def __init__(self, match):
        id, marker, text = match
        super().__init__(marker)
        self.id = id
        self.text = text
