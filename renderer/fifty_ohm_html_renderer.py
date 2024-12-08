import textwrap

from mistletoe import HtmlRenderer

from renderer.comment import BlockComment, SpanComment
from renderer.dash import Dash
from renderer.halfwidth_spaces import HalfwidthSpaces
from renderer.nonbreaking_spaces import NonbreakingSpaces, NonbreakingSpacesDots
from renderer.quote import Quote
from renderer.references import References
from renderer.tag import Tag
from renderer.underline import Underline
from renderer.unit import Unit

units = {
    "A": "A",
    "Ah": "Ah",
    "A/mm²": "A/mm²",
    "baud": "baud",
    "Bit": "Bit",
    "Bit/s": "Bit/s",
    "dB": "dB",
    "dBi": "dBi",
    "dBm": "dBm",
    "dBW": "dBW",
    "F": "F",
    "J": "J",
    "Hz": "Hz",
    "H": "H",
    "cm": "cm",
    "m": "m",
    "m²": "m²",
    "ppm": "ppm",
    "pps": "pps",
    "s": "s",
    "V": "V",
    "W": "W",
    "Wh": "Wh",
    "°": "°",
    "%": "%",
}

no_space_units = ["°", "%"]


class FiftyOhmHtmlRenderer(HtmlRenderer):
    margin_anchor_id = 0
    margin_id = 0
    section_url = "section.html"
    ref_id = 0

    def __init__(self):
        super().__init__(
            Dash,
            BlockComment,
            SpanComment,
            Quote,
            Unit,
            Underline,
            Tag,
            HalfwidthSpaces,
            NonbreakingSpaces,
            NonbreakingSpacesDots,
            HalfwidthSpaces,
            NonbreakingSpaces,
            NonbreakingSpacesDots,
            References,
        )

    def render_dash(self, token):
        return " &ndash; "

    def render_block_comment(self, token):
        return ""

    def render_span_comment(self, token):
        return ""

    def render_quote(self, token):
        return f"„{self.render_inner(token)}“"

    def render_underline(self, token):
        return f"<u>{self.render_inner(token)}</u>"

    @staticmethod
    def render_unit(token):
        unit = token.prefix + units[token.unit]
        if token.unit in no_space_units:
            return f"{token.value}{unit}"
        else:
            return f"{token.value}&#8239;{unit}"

    def render_thematic_break(self, token):
        self.margin_anchor_id += 1
        return f'<a id="margin_{self.margin_anchor_id}"></a>'

    @staticmethod
    def render_tag_helper(type, content, margin_id, margin_anchor_id):
        """This function is used to render the different types of tags. It is
        used in the HtmlRenderer class and also in the test class"""
        return textwrap.dedent(f"""\
            <div class="margin {type}" id="margin_for_{margin_id}">
                {content}
            </div>
            <a id="margin_orig_{margin_id}"></a>
            <script>
            (() => {{
                function moveFunc() {{
                    const targetEl = document.getElementById(
                        window.innerWidth > 800 ? "margin_{margin_anchor_id}" : "margin_orig_{margin_id}"
                    );
                    targetEl.parentNode.insertBefore(
                        document.getElementById("margin_for_{margin_id}"),
                        targetEl
                    );
                }}
                addEventListener("resize", moveFunc);
                moveFunc();
            }})();
            </script>
        """)

    def render_tag(self, token):
        if token.tagtype == "latexonly":
            return ""
        elif token.tagtype == "webonly":
            return self.render_inner(token)

        self.margin_id += 1

        if token.tagtype == "webmargin":
            type = "margin"
        elif token.tagtype == "webtipp":
            type = "tipp"
        elif token.tagtype == "webindepth":
            type = "indepth"
        else:
            type = token.tagtype

        return self.render_tag_helper(
            type, self.render_inner(token), self.margin_id, self.margin_anchor_id
        )

    def render_halfwidth_spaces(self, token):
        return f"{token.first}.&#8239;{token.second}."

    def render_nonbreaking_spaces(self, token):
        return f"{token.first}&#160;{token.second}"

    def render_nonbreaking_spaces_dots(self, token):
        lookup = {"": "", " ": "&#160;"}
        return f"{lookup[token.first]}{token.second}{lookup[token.third]}"

    def render_references(self, token):
        return f'<a href="{self.section_url}#ref_{token.first}" onclick="highlightRef(\'{token.first}\');">{self.ref_id}</a>'
