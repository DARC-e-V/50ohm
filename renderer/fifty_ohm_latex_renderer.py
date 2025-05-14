from mistletoe.latex_renderer import LaTeXRenderer

from .comment import BlockComment
from .dash import Dash
from .halfwidth_spaces import HalfwidthSpaces
from .nonbreaking_spaces import NonbreakingSpaces, NonbreakingSpacesDots
from .photo import Photo
from .picture import Picture
from .question import Question
from .quote import Quote
from .tag import Tag
from .underline import Underline


class FiftyOhmLaTeXRenderer(LaTeXRenderer):
    def __init__(self, question_renderer=None):
        super().__init__(
            Dash,
            BlockComment,
            Quote,
            Underline,
            Tag,
            HalfwidthSpaces,
            NonbreakingSpaces,
            NonbreakingSpacesDots,
            Question,
            Picture,
            Photo
        )
        self.question_renderer = question_renderer

    def render_document(self, token):
        self.footnotes.update(token.footnotes)
        return self.render_inner(token)

    def render_dash(self, token):
        return " -- "

    def render_block_comment(self, token):
        return f"% {token.content}\n"

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

    def render_question(self, token):
        return self.question_renderer(token.question_number)

    @staticmethod
    def render_picture_helper(id, ref, text, number):
        return rf"""\DARCimage{{1.0\linewidth}}{{{id}include}}
\captionof{{figure}}{{{text}}}
\label{{{ref}}}"""

    def render_picture(self, token) :
        return self.render_picture_helper(token.id, token.ref, token.text, token.number)

    @staticmethod
    def render_photo_helper(id, ref, text, number):
        return rf"""\includegraphics[width=1.0\linewidth]{{photo/{id}}}
\captionof{{figure}}{{{text}}}
\label{{{ref}}}"""

    def render_photo(self, token) :
        return self.render_photo_helper(token.id, token.ref, token.text, token.number)