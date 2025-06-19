from mistletoe import Document

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer

from .slide_break import SlideBreak


class FiftyOhmHtmlSlideRenderer(FiftyOhmHtmlRenderer):
    def __init__(self, **kwargs):
        super().__init__(
            SlideBreak,
            **kwargs,
        )
    
    def render_wrapper(self, content):
        content = "---\n" + content
        return super().render(Document(content))

    def render_slide_break(self, token):
        inner = self.render_inner(token)

        if token.attribute is None:
            return f"<section>\n{inner}\n</section>\n"
        else:
            return f"<section {token.attribute}>\n{inner}\n</section>\n"

    def render_qso(self, token):
        qso = '<div class="qso r-fit-text">\n'
        for child in token.children:
            direction = "other" if child.received else "own"
            fade = "fragment fade-left" if child.received else "fragment fade-right"
            qso += f'<div class="qso_{direction} {fade}">{self.render_inner(child)}</div>\n'
        qso += "</div>\n"
        return qso

    def render_tag(self, token):
        if token.tagtype == "fragment":
            return f'<div class="fragment">\n{self.render_inner(token)}\n</div>\n'
        if token.tagtype == "left":
            return f'<div id="left">\n{self.render_inner(token)}\n</div>\n'
        if token.tagtype == "right":
            return f'<div id="right">\n{self.render_inner(token)}\n</div>\n'
        elif token.tagtype == "note":
            return f'<aside class="notes">\n{self.render_inner(token)}\n</aside>\n'

        return ""  # Ignore other tags in slide context anyway in tokenizer
