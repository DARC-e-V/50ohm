import mistletoe.token
from mistletoe.block_token import BlockToken


class ReferencedToken(BlockToken):
    line_number: int = -1
    marker: str = None
    label: str = None

    def __init__(self, marker: str):
        self.marker = marker

        if marker not in mistletoe.token._root_node.references:
            self.label = len(mistletoe.token._root_node.references) + 1
            mistletoe.token._root_node.references[marker] = self.label
        else:
            self.label = mistletoe._root_node.references[marker]
