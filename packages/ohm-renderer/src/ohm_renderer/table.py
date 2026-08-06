import re
from contextlib import suppress
from enum import StrEnum
from itertools import zip_longest

from mistletoe import block_token

from ohm_renderer.referenced_token import ReferencedToken


def unregister_gfm_table() -> None:
    """Unregisters mistletoe's own table token, to be called after registering ours.

    Required to avoid errors with the original Table token matching, but calling our
    overridden render functions.
    """
    with suppress(ValueError):
        block_token.remove_token(block_token.Table)


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
        """Builds a row from already split cell contents, see ``split``.

        Unlike ``block_token.TableRow`` this takes the cells and not the raw line,
        because the header's cells have their alignment prefixes stripped by
        ``Table.parse_alignment`` first, and body cells must not go through that.
        """
        self.row_alignment = row_alignment or [None]
        self.line_number = line_number
        # The header defines the column count, so a shorter row is padded with empty
        # cells and any surplus cell is dropped.
        self.children = [
            TableCell(cell or "", alignment, line_number)
            for cell, alignment in zip_longest(cells[: len(self.row_alignment)], self.row_alignment)
        ]

    @property
    def row_align(self) -> list[int | None]:
        return [MISTLETOE_ALIGNMENT.get(alignment) for alignment in self.row_alignment]

    @classmethod
    def split(cls, line: str) -> list[str]:
        cells = cls.split_pattern.split(line.strip())
        # Outer pipes produce empty entries, but they are not real cells and need to be removed from the output.
        # TODO: Check edge case ||cell| -> should generate 2 cells
        if cells and cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]

        return [cls.escaped_pipe_pattern.sub("\\1|", cell.strip()) for cell in cells]


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
    def check_interrupts_paragraph(cls, lines):
        return cls.start(lines.peek())

    @classmethod
    def read(cls, lines):
        line_buffer = [next(lines)]
        start_line = lines.line_number()

        name = ""
        caption = ""

        # Read table until the end: No more column definitions, caption, or empty line.
        next_line = lines.peek()
        while next_line is not None and next_line.strip() != "":
            maybe_caption = cls.caption_pattern.match(next_line.strip())
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

        cells, alignment = self.parse_alignment(lines[0])
        # A header without a single cell still spans one, unaligned column. Without this
        # the table would have no column at all and LaTeX an empty tabularx preamble.
        # TODO: Check if it’s even possible to have an header without a cell.
        self.column_alignment = alignment or [None]
        self.header = TableRow(cells, self.column_alignment, start_line)
        self.children = [
            TableRow(TableRow.split(line), self.column_alignment, start_line + offset)
            for offset, line in enumerate(lines[1:], start=1)
        ]

    @property
    def column_align(self) -> list[int | None]:
        return [MISTLETOE_ALIGNMENT.get(alignment) for alignment in self.column_alignment]
