import mistletoe


class Document(mistletoe.Document):
    def __init__(self, *args, **kwargs):
        # Figures must exist before super().__init__ tokenizes the lines,
        # since Figure reads it from _root_node during tokenization.
        self.figures: dict[str, str] = {}

        super().__init__(*args, **kwargs)
