from renderer.document import Document
from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_html_slide_renderer import FiftyOhmHtmlSlideRenderer


def paragraph(text):
    return f"<p>{text}</p>\n"


def render_html(markdown):
    """Render markdown with the HTML renderer through the project's Document."""
    with FiftyOhmHtmlRenderer() as renderer:
        return renderer.render(Document(markdown))


def render_slide(markdown):
    """Render markdown with the slide renderer through the project's Document."""
    with FiftyOhmHtmlSlideRenderer() as renderer:
        return renderer.render(Document(markdown))
