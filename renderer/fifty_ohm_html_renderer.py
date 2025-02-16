import textwrap

from mistletoe import Document, HtmlRenderer

from .comment import BlockComment
from .dash import Dash
from .halfwidth_spaces import HalfwidthSpaces
from .morse import Morse
from .nonbreaking_spaces import NonbreakingSpaces, NonbreakingSpacesDots
from .quote import Quote
from .references import References
from .tag import Tag
from .underline import Underline
from .unit import Unit


class FiftyOhmHtmlRenderer(HtmlRenderer):
    margin_anchor_id = 0
    margin_id = 0
    section_url = "section.html"
    ref_id = 0

    def __init__(self):
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
            References,
        )

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
                result += '<span class="morse_char">\n'
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
        elif token.tagtype == "webtip":
            type = "tip"
        elif token.tagtype == "webindepth":
            type = "indepth"
        else:
            type = token.tagtype

        return self.render_tag_helper(type, self.render_inner(token), self.margin_id, self.margin_anchor_id)

    def render_halfwidth_spaces(self, token):
        return f"{token.first}.&#8239;{token.second}."

    def render_nonbreaking_spaces(self, token):
        return f"{token.first}&#160;{token.second}"

    def render_nonbreaking_spaces_dots(self, token):
        lookup = {"": "", " ": "&#160;"}
        return f"{lookup[token.first]}{token.second}{lookup[token.third]}"

    def render_references(self, token):
        return f'<a href="{self.section_url}#ref_{token.first}" onclick="highlightRef(\'{token.first}\');">{self.ref_id}</a>'

    def render_document(self, token: Document) -> str:
        self.footnotes.update(token.footnotes)
        # Filter out None values, so block tokens can return None to not be rendered.
        inner = "\n".join(filter(lambda x: x is not None, [self.render(child) for child in token.children]))
        return f"{inner}\n" if inner else ""
