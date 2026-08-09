import re
from collections.abc import Iterable, Iterator

from mistletoe import span_token
from mistletoe.markdown_renderer import Fragment, MarkdownRenderer

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
from .reference import Reference
from .smartquote import Smartquote
from .table import Table, unregister_gfm_table
from .tag import Tag
from .underline import Underline
from .unit import Unit

# Literal whitespace, not HTML entities: MDX passes both through, but the literal
# characters keep the generated Markdown readable and diffable.
NARROW_NBSP = "\u202f"
NBSP = "\u00a0"

TAG_TYPES = {
    "webmargin": "margin",
    "webtip": "tip",
    "webindepth": "indepth",
}

# A "<" only starts a JSX tag when a name or a closing slash follows it.
TAG_START = re.compile(r"<(?=[A-Za-z/])")


class FiftyOhmMdxRenderer(MarkdownRenderer):
    """Renders DARCdown to MDX."""

    units = {
        "Ohm": "Ω",
    }

    def __init__(
        self,
        *extras,
        picture_handler=None,
        photo_handler=None,
        edition=None,
        chapter=None,
        section=None,
        **kwargs,
    ):
        super().__init__(
            Dash,
            BlockComment,
            Smartquote,
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

        self.picture_handler = picture_handler
        self.photo_handler = photo_handler

        self.edition = edition
        self.chapter = chapter
        self.section = section

        self.figures: dict[str, str] = {}

        # Keep track of index ids already emitted in this document.
        self.index_anchor_ids: set[tuple[str, str | None]] = set()

        self.margin_anchor_id = 0

    def _format_figure_label(self, marker: str) -> str:
        """Resolves a figure marker to its label, or to "?" when it is unknown."""
        if marker not in self.figures:
            return "?"

        label = self.figures[marker]
        if self.edition and self.chapter and self.section:
            label = f"{self.edition}-{self.chapter}.{self.section}.{label}"
        return label

    @staticmethod
    def _attr(name: str, value) -> str:
        """Renders a JSX attribute, or nothing at all for an empty value."""
        if value in (None, ""):
            return ""
        escaped = str(value).replace('"', "&quot;")
        return f' {name}="{escaped}"'

    @staticmethod
    def _trim_blank_lines(lines: Iterable[str]) -> list[str]:
        """Drops the blank lines at the start and at the end, keeping those in between."""
        lines = list(lines)
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        return lines

    @classmethod
    def _element(cls, name: str, inner_lines: Iterable[str], attributes: str = "") -> list[str]:
        """Wraps Markdown content in a block-level element."""
        return [f"<{name}{attributes}>", *cls._trim_blank_lines(inner_lines), f"</{name}>"]

    @classmethod
    def fragments_to_lines(cls, fragments: Iterable[Fragment], max_line_length: int | None = None) -> Iterator[str]:
        # Fold lines starting with { into the previous line, to avoid problems with MDX.
        # MDX treats lines starting with { as JSX expressions, which causes troubles for
        # our formulas containing curly braces.
        # TODO: This should be neutral to render, check once formulas are properly implemented.
        # TODO: Try restpecting max_line_length.
        folded: list[str] = []
        for line in super().fragments_to_lines(fragments, max_line_length=max_line_length):
            if folded and line.startswith("{"):
                folded[-1] = f"{folded[-1]} {line}"
            else:
                folded.append(line)
        yield from folded

    def render_document(self, token: Document, max_line_length: int) -> Iterable[str]:
        self.figures.update(token.figures)
        return self._trim_blank_lines(super().render_document(token, max_line_length))

    def render_block_comment(self, token, max_line_length: int) -> Iterable[str]:
        # A comment interrupts a paragraph, so dropping it entirely would merge the two
        # halves into one. It leaves the blank line behind that separated them.
        return [""]

    def render_thematic_break(self, token, max_line_length: int) -> Iterable[str]:
        self.margin_anchor_id += 1
        return [f'<Anchor id="margin_{self.margin_anchor_id}" />']

    def render_question(self, token: Question, max_line_length: int) -> Iterable[str]:
        return [f'<Question number="{token.question_number}" />']

    def render_include(self, token: Include, max_line_length: int) -> Iterable[str]:
        return [f'<Include ident="{token.ident}" />']

    def render_formula(self, token: Formula, max_line_length: int) -> Iterable[str]:
        return ["$$", token.formula.strip(), "$$"]

    def render_tag(self, token: Tag, max_line_length: int) -> Iterable[str]:
        if token.tagtype == "latexonly":
            return []

        inner = self.blocks_to_lines(token.children, max_line_length=max_line_length)
        if token.tagtype == "webonly":
            return self._trim_blank_lines(inner)

        tagtype = TAG_TYPES.get(token.tagtype, token.tagtype)
        return self._element("Tag", inner, self._attr("type", tagtype))

    def render_qso(self, token: Qso, max_line_length: int) -> Iterable[str]:
        lines = []
        for child in token.children:
            # Qso.read turns every source line into a QsoLine, so we ignore blank ones here.
            if not child.text:
                continue
            received = "true" if child.received else "false"
            content = next(self.span_to_lines(child.children, max_line_length=None), "")
            lines.append(f"<QsoLine received={{{received}}}>{content}</QsoLine>")
        return self._element("Qso", lines)

    def render_image(self, token: Image, max_line_length: int | None = None):
        # Passthrough for standard Markdown images until we improve image handling.
        if isinstance(token, span_token.Image):
            return super().render_image(token)

        # Only supported kinds are photo and picture
        if token.kind == "photo":
            handler, source = self.photo_handler, f"/photos/{token.id}.png"
        elif token.kind == "picture":
            handler, source = self.picture_handler, f"/pictures/{token.id}.svg"
        else:
            return []

        alt_text = handler(token.id) if handler else None
        # Collapse whitespace and strip brackets to avoid problems when rendering it into Markdown.
        alt_text = re.sub(r"\s+", " ", (alt_text or "").replace("[", "").replace("]", "")).strip()

        return self.render_figure(token, [f"![{alt_text}]({source})"], "Abbildung", token.kind)

    def render_table(self, token: Table, max_line_length: int) -> Iterable[str]:
        table = list(super().render_table(token, max_line_length))

        # Only a captioned table becomes a figure, the caption pattern always yields a marker too.
        if token.caption == "":
            # Include an empty line after table because otherwise GFM tables swallow the following paragraph.
            return [*table, ""]

        return self.render_figure(token, table, "Tabelle")

    def table_row_to_text(self, row) -> list[str]:
        # Pipes are unescaped while parsing the row, so they have to be escaped again here.
        return [text.replace("|", "\\|") for text in super().table_row_to_text(row)]

    def render_figure(
        self,
        token: Figure,
        inner_lines: Iterable[str],
        caption_prefix: str,
        css_class: str | None = None,
    ) -> list[str]:
        label = self._format_figure_label(token.marker)

        attributes = self._attr("class", css_class)
        if token.marker:
            attributes += self._attr("id", f"ref_{token.marker}")

        caption = f"<figcaption>{caption_prefix} {label}: {token.caption}</figcaption>"

        return self._element("figure", [*inner_lines, "", caption], attributes)

    def render_raw_text(self, token) -> Iterable[Fragment]:
        # Escape "<" when it looks like it’s at the start of a JSX tag.
        # This avoids problems with invalid (unclosed) or unknown tags in the MDX output.
        yield Fragment(TAG_START.sub(r"\\<", token.content), wordwrap=True)

    def render_dash(self, token) -> Iterable[Fragment]:
        # MDX can render this as a em-dash.
        yield Fragment(" -- ")

    def render_smartquote(self, token: Smartquote) -> Iterable[Fragment]:
        # MDX supports smart quotes, which provides better i18n support than we can in here.
        return self.embed_span(Fragment('"'), token.children)

    def render_underline(self, token: Underline) -> Iterable[Fragment]:
        return self.embed_span(Fragment("<u>"), token.children, Fragment("</u>"))

    def render_unit(self, token: Unit) -> Iterable[Fragment]:
        unit = token.prefix + self.units.get(token.unit, token.unit)
        if token.unit in ["°", "%"]:
            # Special cases with no space between value and unit.
            yield Fragment(f"{token.value}{unit}")
        else:
            # Default case is rendered with a narrow no-break space.
            yield Fragment(f"{token.value}{NARROW_NBSP}{unit}")

    def render_halfwidth_spaces(self, token: HalfwidthSpaces) -> Iterable[Fragment]:
        yield Fragment(f"{token.first}.{NARROW_NBSP}{token.second}.")

    def render_nonbreaking_spaces(self, token: NonbreakingSpaces) -> Iterable[Fragment]:
        yield Fragment(f"{token.first}{NBSP}{token.second}")

    def render_nonbreaking_spaces_dots(self, token: NonbreakingSpacesDots) -> Iterable[Fragment]:
        lookup = {"": "", " ": NBSP}
        yield Fragment(f"{lookup[token.first]}{token.second}{lookup[token.third]}")

    def render_morse(self, token: Morse) -> Iterable[Fragment]:
        yield Fragment(f"<Morse{self._attr('text', token.content)} />")

    def render_reference(self, token: Reference) -> Iterable[Fragment]:
        label = self._format_figure_label(token.marker)
        yield Fragment(f"<Reference{self._attr('marker', token.marker)}{self._attr('label', label)} />")

    def render_index(self, token: Index) -> Iterable[Fragment]:
        anchor_id = (token.first, token.second)
        if anchor_id in self.index_anchor_ids:
            return

        self.index_anchor_ids.add(anchor_id)
        yield Fragment(f"<Index{self._attr('first', token.first)}{self._attr('second', token.second)} />")
