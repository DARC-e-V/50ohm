from jinja2 import Environment, FileSystemLoader
from mistletoe import Document

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer

from .qso import Qso
from .slide_break import SlideBreak
from .tag import Tag


class FiftyOhmHtmlSlideRenderer(FiftyOhmHtmlRenderer):

    def __init__(self, question_renderer=None, picture_handler=None, photo_handler=None):
        super().__init__(
            SlideBreak,
            Qso,
            Tag,
            question_renderer=question_renderer,
            picture_handler=picture_handler,
            photo_handler=photo_handler,
        )
        self.env = Environment(loader=FileSystemLoader("templates/slide"))
    
    def render_wrapper(self, content):
        content = "---\n" + content
        return super().render(Document(content))

    def render_slide_break(self, token):
        inner = self.render_inner(token)

        if token.attribute is None:
            return f'<section>\n{inner}\n</section>\n'
        if token.attribute == "attention":
            return f'<section data-background-color="#B8EAFF">\n{inner}\n</section>\n'
        elif token.attribute == "danger":
            return f'<section data-background-color="#FF756D">\n{inner}\n</section>\n'
        elif token.attribute == "unit":
            return f'<section data-background-color="#40C08C">\n{inner}\n</section>\n'
        else:
            return f'<section {token.attribute}>\n{inner}\n</section>\n'

    def render_qso(self, token):
        qso = '<div class="qso r-fit-text">\n'
        for child in token.children:
            direction = "other" if child.received else "own"
            fade = "fragment fade-left" if child.received else "fragment fade-right"
            qso += f'<div class="qso_{direction} {fade}">{self.render_inner(child)}</div>\n'
        qso += '</div>\n'
        return qso

    def render_note(self, token):
        return f'<aside class="notes">\n{self.render_inner(token)}\n</aside>\n'

    def render_tag(self, token):
        if token.tagtype == "fragment":
            return f'<div class="fragment">\n{self.render_inner(token)}\n</div>\n'
        if token.tagtype == "left":
            return f'<div id="left">\n{self.render_inner(token)}\n</div>\n'
        if token.tagtype == "right":
            return f'<div id="right">\n{self.render_inner(token)}\n</div>\n'
        elif token.tagtype == "note":
            return f'<aside class="notes">\n{self.render_inner(token)}\n</aside>\n'
        else:
            return "" # Ignore other tags in slide context

