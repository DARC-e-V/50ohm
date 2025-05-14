
from mistletoe.block_token import BlockToken


class Table(BlockToken):
    @staticmethod
    def start(line):
        return '|' in line

    @classmethod
    def parseHeader(self, line):
        line = line.strip().strip('|') # Remove leading/trailing whitespace and pipes
        columns = [col.strip() for col in line.split('|')] # Split by pipe |

        alignment = []
        data = []

        for column in columns:
            attr, val = column.split(':')
            alignment.append(attr)
            data.append(val)
        
        return data, alignment

    @classmethod
    def parseRow(self, line):
        line = line.strip().strip('|')
        columns = [col.strip() for col in line.split('|')]

        data = []

        for column in columns:
            data.append(column)

        return data

    @classmethod
    def read(self, lines):

        table = []

        header = next(lines)

        data, alignment = self.parseHeader(header)
        table.append([data])

        for line in lines:
            if "|" not in line:
                break
            data = self.parseRow(line)
            table.append([data])

        return [table, alignment]

    def __init__(self, match):
        self.table = match[0]
        self.alignment = match[1]
        print("init")
