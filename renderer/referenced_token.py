import mistletoe.token
from mistletoe.block_token import BlockToken


class ReferencedToken(BlockToken):
    def __init__(self, marker: str):
        if marker != "":
            self.marker = marker
            references = mistletoe.token._root_node.references
            if marker not in references:
                label = str(len(references) + 1)
                references[marker] = label
            else:
                label = references[marker]
            self.label = label
        else:
            self.marker = None
            self.label = None
