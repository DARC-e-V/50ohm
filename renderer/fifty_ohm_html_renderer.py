from mistletoe import HtmlRenderer

from renderer.comment import Comment
from renderer.quote import Quote
from renderer.halfwidth_spaces import HalfwidthSpaces
from renderer.nonbreaking_spaces import NonbreakingSpaces, NonbreakingSpacesDots
from renderer.references import References


class FiftyOhmHtmlRenderer(HtmlRenderer):
    def __init__(self):
        super().__init__(Comment, Quote, HalfwidthSpaces, NonbreakingSpaces, NonbreakingSpacesDots, References)

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
        return f"&#160;{token.first}&#160;"

    def render_references(self, token, dest_id=0, chap_url="DeineMama.html"):
        return f"<a href=&#34;{chap_url}#ref_{token.first}&#34; onclick=&#34;highlightRef(&#39;{token.first}&#39;);&#34;>{dest_id}</a>"