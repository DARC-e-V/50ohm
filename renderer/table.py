import re
from enum import Enum

from mistletoe import span_token
from mistletoe.block_token import BlockToken


class CellAlignment(Enum):
    LEFT = "l"
    CENTER = "c"
    RIGHT = "r"
    EXPAND = "X"


class TableCell(BlockToken):
    alignment: CellAlignment
    header: bool

    @staticmethod
    def start(_):
        return False

    def __init__(self, match, alignment: CellAlignment, header=False):
        super().__init__(match, span_token.tokenize_inner)
        self.alignment, self.header = alignment, header


class TableRow(BlockToken):
    @staticmethod
    def start(_):
        return False

    @classmethod
    def parse(cls, line) -> list[str]:
        line = line.strip().strip("|")
        return [col.strip() for col in line.split("|")]

    def __init__(self, match, alignment: list[CellAlignment]):
        self.children = [TableCell(cell, alignment[i]) for i, cell in enumerate(self.parse(match))]


class TableHeader(TableRow):
    alignment: list[CellAlignment]

    @staticmethod
    def start(_):
        return False

    @classmethod
    def parse(cls, line) -> list[str]:
        alignment: list[CellAlignment] = []
        columns: list[str] = []
        for column in super().parse(line):
            attr: CellAlignment
            value: str
            attr, value = re.match(r"^ ?(?:([lcrX]):)? ?(.*)", column).group(1, 2)

            alignment.append(attr)
            columns.append(value)

        return columns, alignment

    def __init__(self, match):
        columns, self.alignment = self.parse(match)
        self.children = [TableCell(cell, self.alignment[i], True) for i, cell in enumerate(columns)]


class TableBody(BlockToken):
    header: bool

    @staticmethod
    def start(_):
        return False

    def __init__(self, rows: TableRow, header=False):
        self.children, self.header = rows, header


class Table(BlockToken):
    name: str
    caption: str
    header: list[TableHeader]
    rows: list[TableRow]

    @staticmethod
    def start(line):
        return "|" in line

    @classmethod
    def read(cls, lines):
        header = TableHeader(next(lines))
        alignment = header.alignment

        name = ""
        caption = ""
        children = [TableBody([header], True)]

        # Read table until the end: No more column definitions, caption, or empty line.
        line_buffer = []
        next_line = lines.peek()
        while next_line is not None and next_line.strip() != "":
            maybe_caption = re.match(r"\[table:([^:\]]+):([^:\]]+)\]", next_line)
            if maybe_caption is not None:
                name, caption = maybe_caption.group(1, 2)
                next(lines)
                break
            elif "|" not in next_line:
                break
            else:
                line_buffer.append(next(lines))
                next_line = lines.peek()

        children.append(TableBody([TableRow(line, alignment) for line in line_buffer]))

        return children, name, caption

    def __init__(self, match):
        self.children, self.name, self.caption = match
