import re

from mistletoe.block_tokenizer import FileWrapper

from ohm_renderer.referenced_token import ReferencedToken


class Image(ReferencedToken):
    """
    Block token for pictures and photos.
    Examples:
        [picture:727:amplitude_periode_halbwellen:Positive und negative Halbwellen einer Sinusschwingung]
        [photo:123:n_wasserfalldiagramm_trx_collage:Ansichten verschiedener Transceiver]
    """

    pattern = re.compile(r"^\[(?P<kind>picture|photo):(?P<id>\d+):(?P<marker>[^:\]]+):(?P<text>[^:\]]+)\]$")

    @classmethod
    def start(cls, line: str):
        return cls.pattern.match(line.strip()) is not None

    @classmethod
    def check_interrupts_paragraph(cls, lines: FileWrapper):
        line = lines.peek()
        if line is not None:
            return cls.start(line)
        else:
            return False

    @classmethod
    def read(cls, lines: FileWrapper):
        match = cls.pattern.match(next(lines).strip())
        return match.group("kind"), match.group("id"), match.group("marker"), match.group("text")

    def __init__(self, match):
        kind, id, marker, text = match
        super().__init__(marker)
        self.kind = kind
        self.id = id
        self.text = text
