import mistletoe.token
from mistletoe.block_token import BlockToken


class Figure(BlockToken):
    """Base for tokens rendered as a figure with a numbered caption.

    Every figure shares a single, document-wide counter, so pictures, photos and
    tables are numbered in document order. An empty marker leaves the token
    unnumbered and consumes no counter slot.
    """

    def __init__(self, marker: str, caption: str):
        self.caption = caption
        if marker != "":
            self.marker = marker
            figures = mistletoe.token._root_node.figures
            if marker not in figures:
                label = str(len(figures) + 1)
                figures[marker] = label
            else:
                label = figures[marker]
            self.label = label
        else:
            self.marker = None
            self.label = None
