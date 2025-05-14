import re

from mistletoe import span_token
from mistletoe.block_token import BlockToken


class Table(BlockToken):
    @staticmethod
    def start(line):
        return "|" in line

    @classmethod
    def parse_header(cls, line):
        # Parse header, extract alignment and make an ordinary row out of it
        line = line.strip().strip("|")  # Remove leading/trailing whitespace and pipes
        columns = [col.strip() for col in line.split("|")]  # Split by pipe |

        alignment = []
        header = "| "

        for column in columns:
            attr, val = re.match(r"^ ?(?:([lcrX]):)?(.*)", column).group(1, 2)
            alignment.append(attr)
            header += val + " | "

        return header, alignment

    @classmethod
    def read(cls, lines):
        header = next(lines)
        header, alignment = cls.parse_header(header)
        name = ""
        caption = ""
        rows = [TableRow(header)]

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

        rows.extend([TableRow(line) for line in line_buffer])

        return alignment, rows, name, caption

    def __init__(self, match):
        self.alignment, self.children, self.name, self.caption = match


class TableRow(BlockToken):
    @classmethod
    def parse_row(cls, line):
        line = line.strip().strip("|")
        columns = [col.strip() for col in line.split("|")]

        data = []

        for column in columns:
            data.append(TableCell(column))

        return data

    def __init__(self, match):
        self.children = self.parse_row(match)


class TableCell(BlockToken):
    def __init__(self, match):
        super().__init__(match, span_token.tokenize_inner)
