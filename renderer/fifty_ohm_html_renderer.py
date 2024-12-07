from mistletoe import HtmlRenderer

from renderer.comment import Comment
from renderer.tag import Tag
from renderer.quote import Quote
from renderer.underline import Underline


class FiftyOhmHtmlRenderer(HtmlRenderer):
    def __init__(self):
        super().__init__(Comment, Quote, Underline, Tag)

    def render_comment():
        return None

    def render_quote(self, token):
        return f"„{self.render_inner(token)}“"

    def render_underline(self, token):
        return f"<u>{self.render_inner(token)}</u>"

    def render_tag(self, token):
        return f'<div class="{token.tagtype}">{self.render_inner(token)}</div>'