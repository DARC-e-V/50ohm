import textwrap

from mistletoe import HtmlRenderer

from renderer.comment import BlockComment, SpanComment
from renderer.dash import Dash
from renderer.quote import Quote
from renderer.tag import Tag
from renderer.underline import Underline


class FiftyOhmHtmlRenderer(HtmlRenderer):

    margin_anchor_id = 0
    margin_id = 0

    def __init__(self):
        super().__init__(Dash, BlockComment, SpanComment, Quote, Underline, Tag)

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

    def render_thematic_break(self, token):
        self.margin_anchor_id += 1
        return f'<a id="margin_{self.margin_anchor_id}"></a>'

    @staticmethod
    def render_tag_helper(type, content, margin_id, margin_anchor_id):
        """ This function is used to render the different types of tags. It is
        used in the HtmlRenderer class and also in the test class """
        return textwrap.dedent(f'''\
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
        ''')

    def render_tag(self, token):
        if(token.tagtype == "latexonly"):
            return ""
        elif(token.tagtype == "webonly"):
            return self.render_inner(token)

        self.margin_id += 1

        if(token.tagtype == "webmargin"):
            type = "margin"
        elif(token.tagtype == "webtipp"):
            type = "tipp"
        elif(token.tagtype == "webindepth"):
            type = "indepth"
        else :
            type = token.tagtype

        return self.render_tag_helper(
            type,
            self.render_inner(token),
            self.margin_id,
            self.margin_anchor_id
        )
    