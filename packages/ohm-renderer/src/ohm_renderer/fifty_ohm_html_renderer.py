import re
from importlib.resources import files
from textwrap import indent

from jinja2 import Environment, FileSystemLoader
from mistletoe import HtmlRenderer

from .comment import BlockComment
from .dash import Dash
from .document import Document
from .figure import Figure
from .formula import Formula
from .halfwidth_spaces import HalfwidthSpaces
from .image import Image
from .include import Include
from .index import Index
from .morse import Morse
from .nonbreaking_spaces import NonbreakingSpaces, NonbreakingSpacesDots
from .qso import Qso
from .question import Question
from .quote import Quote
from .reference import Reference
from .table import CellAlignment, Table, TableCell, unregister_gfm_table
from .tag import Tag
from .underline import Underline
from .unit import Unit

# Columns without an explicit alignment and the expanding column have no HTML
# counterpart and stay unaligned, so look this up with ``get``.
table_alignment = {
    CellAlignment.LEFT: "left",
    CellAlignment.CENTER: "center",
    CellAlignment.RIGHT: "right",
}


class FiftyOhmHtmlRenderer(HtmlRenderer):
    margin_anchor_id = 0
    margin_id = 0

    def __init__(
        self,
        *extras,
        question_renderer=None,
        picture_handler=None,
        photo_handler=None,
        include_handler=None,
        edition=None,
        chapter=None,
        section=None,
        section_url=None,
        **kwargs,
    ):
        super().__init__(
            Dash,
            BlockComment,
            Quote,
            Unit,
            Underline,
            Morse,
            Tag,
            HalfwidthSpaces,
            NonbreakingSpaces,
            NonbreakingSpacesDots,
            Reference,
            Question,
            Image,
            Table,
            Qso,
            Include,
            Formula,
            Index,
            *extras,
            **kwargs,
        )
        unregister_gfm_table()

        self.question_renderer = question_renderer
        self.picture_handler = picture_handler
        self.photo_handler = photo_handler
        self.include_handler = include_handler

        # Figure numbering context
        self.edition = edition
        self.chapter = chapter
        self.section = section

        # Set section URL if provided, otherwise use default
        self.section_url = section_url if section_url is not None else "section.html"

        self.figures: dict[str, str] = {}

        # Keep track of index ids already emitted in this document.
        self.index_anchor_ids = set()

    def _format_figure_label(self, marker: str):
        if marker in self.figures:
            label = self.figures[marker]
            if self.edition and self.chapter and self.section:
                label = f"{self.edition}-{self.chapter}.{self.section}.{label}"
            return label
        else:
            return None

    def render_dash(self, token):
        return " &ndash; "

    def render_block_comment(self, token):
        return None

    def render_quote(self, token):
        return f"„{self.render_inner(token)}“"

    def render_underline(self, token):
        return f"<u>{self.render_inner(token)}</u>"

    @classmethod
    def render_unit(cls, token: Unit):
        unit = token.prefix + cls.convert_unit_helper(token.unit)
        if token.unit in ["°", "%"]:
            # Special cases with no space between value and unit.
            return f"{token.value}{unit}"
        else:
            # Default case is rendered with a narrow no-break space.
            return f"{token.value}&#8239;{unit}"

    units = {
        "Ohm": "Ω",
    }

    @classmethod
    def convert_unit_helper(cls, unit: str) -> str:
        """Converts human-typable units to their preferred representation.

        :param str unit: The unit to convert
        """
        if unit in cls.units.keys():
            return cls.units[unit]
        else:
            return unit

    def render_thematic_break(self, token):
        self.margin_anchor_id += 1
        return f'<a id="margin_{self.margin_anchor_id}"></a>'

    @staticmethod
    def render_morse_helper(morse_code):
        result = '<span class="morse">'
        for char in morse_code:
            result += '<span class="morse_char">\n'
            for symbol in char:
                result += '<span class="morse_symbol">\n'
                if symbol == 1:
                    result += "▄"
                elif symbol == 2:
                    result += "▄▄▄"
                elif symbol == 3:
                    result += "&nbsp;"
                result += "</span>\n"
            result += "</span>\n"
        result += "</span>"

        return result

    def render_morse(self, token):
        morse_code = Morse.convert_to_morse_code(token.content)
        return self.render_morse_helper(morse_code)

    @staticmethod
    def render_tag_helper(type, content, margin_id, margin_anchor_id):
        """This function is used to render the different types of tags. It is
        used in the HtmlRenderer class and also in the test class"""
        env = Environment(loader=FileSystemLoader(files("ohm_renderer") / "templates"))
        margin_template = env.get_template("margin.html")
        return margin_template.render(
            type=type,
            content=content,
            id=margin_id,
            margin_anchor_id=margin_anchor_id,
        )

    def render_tag(self, token):
        if token.tagtype == "latexonly":
            return ""
        elif token.tagtype == "webonly":
            return self.render_inner(token)

        self.margin_id += 1

        if token.tagtype == "webmargin":
            type = "margin"
        elif token.tagtype == "webtip":
            type = "tip"
        elif token.tagtype == "webindepth":
            type = "indepth"
        else:
            type = token.tagtype

        return self.render_tag_helper(type, self.render_inner(token), self.margin_id, self.margin_anchor_id)

    def render_qso(self, token):
        self.margin_id += 1
        qso = ""
        for child in token.children:
            direction = "other" if child.received else "own"
            qso += f'<div class="qso_{direction}">{self.render_inner(child)}</div>\n'
        return self.render_tag_helper("qso", qso, self.margin_id, self.margin_anchor_id)

    def render_halfwidth_spaces(self, token):
        return f"{token.first}.&#8239;{token.second}."

    def render_nonbreaking_spaces(self, token):
        return f"{token.first}&#160;{token.second}"

    def render_nonbreaking_spaces_dots(self, token):
        lookup = {"": "", " ": "&#160;"}
        return f"{lookup[token.first]}{token.second}{lookup[token.third]}"

    def render_reference(self, token: Reference):
        # Look up the figure number from the map
        label = self._format_figure_label(token.marker) or "?"
        return (
            f'<a href="{self.section_url}#ref_{token.marker}" onclick="highlightRef(\'{token.marker}\');">{label}</a>'
        )

    def render_question(self, token):
        return self.question_renderer(token.question_number)

    def render_document(self, token: Document) -> str:
        self.figures.update(token.figures)
        self.footnotes.update(token.footnotes)
        inner = self.render_inner(token, "\n")
        return f"{inner}\n" if inner else ""

    def render_inner(self, token, base="") -> str:
        # Filter out None values, so block tokens can return None to not be rendered.
        return base.join(filter(lambda x: x is not None, [self.render(child) for child in token.children]))

    def render_figure(self, token: Figure, inner: str, caption_prefix: str, css_class: str | None = None) -> str:
        label = self._format_figure_label(token.marker) or "?"

        attributes = f' class="{css_class}"' if css_class else ""
        if token.marker:
            attributes += f' id="ref_{token.marker}"'

        body = f"{inner}\n<figcaption>{caption_prefix} {label}: {token.caption}</figcaption>"

        return f"<figure{attributes}>\n{indent(body, '  ')}\n</figure>"

    def render_image(self, token: Image):
        # Only supported kinds are photo and picture
        if token.kind == "photo":
            handler, source = self.photo_handler, f"photos/{token.id}.png"
        elif token.kind == "picture":
            handler, source = self.picture_handler, f"pictures/{token.id}.svg"
        else:
            return ""

        alt_text = handler(token.id) or "" if handler is not None else ""

        # The kind doubles as the figure's class, so pictures and photos stay styleable apart.
        return self.render_figure(token, f'<img src="{source}" alt="{alt_text}">', "Abbildung", token.kind)

    def render_table(self, token: Table):
        table = '<table class="table table-hover">\n'
        table += f"<thead>\n{self.render_table_row(token.header, is_header=True)}</thead>\n"
        if token.children:
            table += f"<tbody>\n{self.render_inner(token)}</tbody>\n"
        table += "</table>"

        # Only a captioned table becomes a figure, the caption pattern always yields a marker too.
        if token.caption == "":
            return table

        return self.render_figure(token, table, "Tabelle")

    def render_table_cell(self, token: TableCell, in_header=False):
        tag = "th" if in_header else "td"
        alignment = table_alignment.get(token.alignment)
        style = f' style="text-align: {alignment};"' if alignment else ""
        return f"<{tag}{style}>{self.render_inner(token)}</{tag}>\n"

    def render_include(self, token):
        return self.include_handler(token.ident)

    def render_formula(self, token):
        return f"\n$${token.formula}$$\n"

    @staticmethod
    def _normalize_index_part(value: str) -> str:
        normalized = value.strip().lower()
        normalized = re.sub(r"\s+", "_", normalized)
        normalized = re.sub(r"[^\w]", "_", normalized)
        normalized = re.sub(r"_+", "_", normalized).strip("_")
        return normalized or "index"

    def render_index(self, token):
        first = self._normalize_index_part(token.first)
        if token.second:
            second = self._normalize_index_part(token.second)
            span_id = f"index_{first}__{second}"
        else:
            span_id = f"index_{first}"

        if span_id in self.index_anchor_ids:
            return ""

        self.index_anchor_ids.add(span_id)
        return f'<span id="{span_id}" class="index-anchor" aria-hidden="true"></span>'
