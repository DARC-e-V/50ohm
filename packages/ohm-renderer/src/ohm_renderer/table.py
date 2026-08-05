import re
from enum import StrEnum
from itertools import zip_longest

from mistletoe import block_token

from ohm_renderer.referenced_token import ReferencedToken


class CellAlignment(StrEnum):
    """Column alignments, with tabularx identifiers for simplified LaTeX support."""

    LEFT = "l"
    CENTER = "c"
    RIGHT = "r"
    EXPAND = "X"


# Mistletoe encodes alignment as None (left), 0 (center) and 1 (right).
MISTLETOE_ALIGNMENT = {CellAlignment.CENTER: 0, CellAlignment.RIGHT: 1}


class TableCell(block_token.TableCell):
    def __init__(self, content, alignment: CellAlignment | None = None, line_number=None):
        self.alignment = alignment
        super().__init__(content, MISTLETOE_ALIGNMENT.get(alignment), line_number)


class TableRow(block_token.TableRow):
    def __init__(
        self,
        cells: list[str],
        row_alignment: list[CellAlignment | None] | None = None,
        line_number=None,
    ):
        self.row_alignment = row_alignment or [None]
        self.line_number = line_number
        self.children = [
            TableCell(cell or "", alignment, line_number) for cell, alignment in zip_longest(cells, self.row_alignment)
        ]

    @property
    def row_align(self) -> list[int | None]:
        """The row alignment in mistletoe's encoding, for its own render functions."""
        return [MISTLETOE_ALIGNMENT.get(alignment) for alignment in self.row_alignment]

    @classmethod
    def split(cls, line: str) -> list[str]:
        """Splits a table line into its cell contents, honouring escaped pipes."""
        return [
            cls.escaped_pipe_pattern.sub("\\1|", cell.strip())
            for cell in filter(None, cls.split_pattern.split(line.strip()))
        ]


class Table(ReferencedToken, block_token.Table):
    alignment_pattern = re.compile(r"^ ?(?:([lcrX]):)? ?(.*)")
    caption_pattern = re.compile(r"\[table:([^:\]]+):([^:\]]+)\]")

    @staticmethod
    def start(line):
        return line.lstrip().startswith("|")

    @classmethod
    def parse_alignment(cls, line: str) -> tuple[list[str], list[CellAlignment | None]]:
        cells: list[str] = []
        alignment: list[CellAlignment | None] = []
        for cell in TableRow.split(line):
            prefix, content = cls.alignment_pattern.match(cell).group(1, 2)
            cells.append(content)
            alignment.append(CellAlignment(prefix) if prefix else None)

        return cells, alignment

    @classmethod
    def read(cls, lines):
        # Mistletoe probes for an interrupting table by calling read() on any
        # paragraph line, so a line that starts no table has to be rejected here.
        next_line = lines.peek()
        if next_line is None or not cls.start(next_line):
            return None

        line_buffer = [next(lines)]
        start_line = lines.line_number()

        name = ""
        caption = ""

        # Read table until the end: No more column definitions, caption, or empty line.
        next_line = lines.peek()
        while next_line is not None and next_line.strip() != "":
            maybe_caption = cls.caption_pattern.match(next_line)
            if maybe_caption is not None:
                name, caption = maybe_caption.group(1, 2)
                next(lines)
                break
            elif "|" not in next_line:
                break
            else:
                line_buffer.append(next(lines))
                next_line = lines.peek()

        return line_buffer, start_line, name, caption

    def __init__(self, match):
        lines, start_line, name, caption = match
        super().__init__(name)
        self.name = name
        self.caption = caption

        cells, self.column_alignment = self.parse_alignment(lines[0])
        self.header = TableRow(cells, self.column_alignment, start_line)
        self.children = [
            TableRow(TableRow.split(line), self.column_alignment, start_line + offset)
            for offset, line in enumerate(lines[1:], start=1)
        ]

    @property
    def column_align(self) -> list[int | None]:
        return [MISTLETOE_ALIGNMENT.get(alignment) for alignment in self.column_alignment]
