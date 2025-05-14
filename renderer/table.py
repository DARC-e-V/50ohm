
from mistletoe import span_token
from mistletoe.block_token import BlockToken


class Table(BlockToken):
    @staticmethod
    def start(line):
        return '|' in line

    @classmethod
    def parse_header(cls, line): 
        # Parse header, extract alignment and make an ordinary row out of it
        line = line.strip().strip('|') # Remove leading/trailing whitespace and pipes
        columns = [col.strip() for col in line.split('|')] # Split by pipe |

        alignment = []
        header = "| "

        for column in columns:
            attr, val = column.split(':')
            alignment.append(attr)
            header += val + " | "
        
        return header, alignment

    @classmethod
    def read(cls, lines):
        header = next(lines)
        header, alignment = cls.parse_header(header)
        rows = [TableRow(header)]

        for line in lines:
            if "|" not in line :
                break
            else :
                rows.append(TableRow(line))

        return alignment, rows

    def __init__(self, match):
        self.alignment, self.children = match


class TableRow(BlockToken):
    @classmethod
    def parse_row(cls, line):
        line = line.strip().strip('|')
        columns = [col.strip() for col in line.split('|')]

        data = []

        for column in columns:
            data.append(TableCell(column))

        return data

    def __init__(self, match):
        self.children = self.parse_row(match)

class TableCell(BlockToken) :
    def __init__(self, match):
        super().__init__(match, span_token.tokenize_inner)
