from mistletoe.latex_renderer import LaTeXRenderer

from renderer.comment import BlockComment, SpanComment
from renderer.dash import Dash
from renderer.halfwidth_spaces import HalfwidthSpaces
from renderer.nonbreaking_spaces import NonbreakingSpaces, NonbreakingSpacesDots
from renderer.quote import Quote
from renderer.tag import Tag
from renderer.underline import Underline


class FiftyOhmLaTeXRenderer(LaTeXRenderer):
    def __init__(self):
        super().__init__(
            Dash,
            BlockComment,
            SpanComment,
            Quote,
            Underline,
            Tag,
            HalfwidthSpaces,
            NonbreakingSpaces,
            NonbreakingSpacesDots,
        )

    def render_document(self, token):
        self.footnotes.update(token.footnotes)
        return self.render_inner(token)

    def render_dash(self, token):
        return " -- "

    def render_block_comment(self, token):
        return ""  # TODO propagate comments to the LaTeX document

    def render_span_comment(self, token):
        return ""  # TODO propagate comments to the LaTeX document

    def render_quote(self, token):
        return rf"\enquote{{{self.render_inner(token)}}}"

    def render_emphasis(self, token):
        return rf"\emph{{{self.render_inner(token)}}}"

    def render_underline(self, token):
        return rf"\underline{{{self.render_inner(token)}}}"

    def render_thematic_break(self, token):
        return ""

    def render_tag(self, token):  # noqa: C901
        tagtype = None

        match token.tagtype:
            case "danger":
                tagtype = "MarginDanger"
            case "warning":
                tagtype = "MarginWarning"
            case "attention":
                tagtype = "MarginAttention"
            case "tip":
                tagtype = "MarginTip"
            case "webtip":
                tagtype = "WebTip"
            case "unit":
                tagtype = "MarginUnit"
            case "indepth":
                tagtype = "MarginInDepth"
            case "webindepth":
                tagtype = "MarginWebInDepth"
            case "webmargin":
                tagtype = "WebMargin"
            case "fullwidth":
                tagtype = "FullWidth"
            case "latexonly":
                return self.render_inner(token)
            case "webonly":
                return ""
            case _:
                tagtype = "Margin"

        return rf"\{tagtype}{{{self.render_inner(token)}}}"

    def render_halfwidth_spaces(self, token):
        return f"{token.first}.\,{token.second}."

    def render_nonbreaking_spaces(self, token):
        return f"{token.first}~{token.second}"

    def render_nonbreaking_spaces_dots(self, token):
        lookup = {"": "", " ": "~"}
        return f"{lookup[token.first]}{token.second}{lookup[token.third]}"
