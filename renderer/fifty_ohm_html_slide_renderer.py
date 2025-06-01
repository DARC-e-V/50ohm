from mistletoe import Document

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer

from .slide_break import SlideBreak


class FiftyOhmHtmlSlideRenderer(FiftyOhmHtmlRenderer):

    def __init__(self, question_renderer=None, picture_handler=None, photo_handler=None):
        super().__init__(
            SlideBreak,
            question_renderer=question_renderer,
            picture_handler=picture_handler,
            photo_handler=photo_handler,
        )
    
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

