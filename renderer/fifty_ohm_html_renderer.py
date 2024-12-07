from mistletoe import HtmlRenderer

from renderer.comment import Comment
from renderer.quote import Quote


class FiftyOhmHtmlRenderer(HtmlRenderer):
    def __init__(self):
        super().__init__(Comment, Quote)

    def render_comment():
        return None

    def render_quote(self, token):
        return f"„{self.render_inner(token)}“"

    def render_underline(self, token):
        return f"<u>{self.render_inner(token)}</u>"