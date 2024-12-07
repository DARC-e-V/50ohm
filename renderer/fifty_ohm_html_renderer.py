from mistletoe import HtmlRenderer

from renderer.comment import Comment
from renderer.quote import Quote
from renderer.halfwidth_spaces import HalfwidthSpaces
from renderer.nonbreaking_spaces import NonbreakingSpaces, NonbreakingSpacesDots


class FiftyOhmHtmlRenderer(HtmlRenderer):
    def __init__(self):
        super().__init__(Comment, Quote, HalfwidthSpaces, NonbreakingSpaces, NonbreakingSpacesDots)

    def render_comment():
        return None

    def render_quote(self, token):
        return f"„{self.render_inner(token)}“"

    def render_underline(self, token):
        return f"<u>{self.render_inner(token)}</u>"
    
    def render_halfwidth_spaces(self, token):
        return f"{token.first}.&#8239;{token.second}."

    def render_nonbreaking_spaces(self, token):
        return f"{token.first}&#160;{token.second}"

    def render_nonbreaking_spaces_dots(self, token):
        lookup = {
            "" : "",
            " " : "&#160;"
        }
        return f"{lookup[token.first]}{token.second}{lookup[token.third]}"