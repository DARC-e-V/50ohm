from mistletoe.block_token import BlockToken


class Comment(BlockToken):
    @staticmethod
    def start(line):
        return line.startswith("%")

    @classmethod
    def read(cls, lines):
        next(lines)
        return None