import mistletoe
import pytest

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from test.util import paragraph


@pytest.mark.html
def test_photo_html():
    assertions = {
        "[photo:123:abc:Text]": FiftyOhmHtmlRenderer.render_photo_helper("123", "abc", "Text", 1),
    }

    for assertion in assertions:
        # Pass figure_number as a list for proper counter management
        with FiftyOhmHtmlRenderer(figure_number=[0]) as renderer:
            from mistletoe import Document

            result = renderer.render(Document(assertion))
            assert result == paragraph(assertions[assertion])


@pytest.mark.latex
def test_photo_latex():
    assertions = {
        "[photo:123:abc:Text]": FiftyOhmLaTeXRenderer.render_photo_helper("123", "abc", "Text", 1),
    }

    for assertion in assertions:
        # Pass figure_number as a list for proper counter management
        with FiftyOhmLaTeXRenderer(figure_number=[0]) as renderer:
            result = renderer.render_document(mistletoe.Document(assertion))
            assert result == "\n" + assertions[assertion] + "\n"
