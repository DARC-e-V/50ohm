import mistletoe


class Document(mistletoe.Document):
    def __init__(self, *args, **kwargs):
        # references must exist before super().__init__ tokenizes the lines,
        # since ReferencedToken reads it from _root_node during tokenization.
        self.references: dict[str, str] = {}

        super().__init__(*args, **kwargs)
