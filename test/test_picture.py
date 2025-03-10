import mistletoe
import pytest

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from test.util import paragraph


@pytest.mark.html
def test_picture_html():
    assertions = {
        "[picture:123:abc:Text]": FiftyOhmHtmlRenderer.render_picture_helper("123", "abc", "Text", "TODO"),
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == paragraph(assertions[assertion])


@pytest.mark.latex
def test_picture_latex():
    assertions = {
        "[picture:123:abc:Text]": FiftyOhmLaTeXRenderer.render_picture_helper("123", "abc", "Text", "TODO"),
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmLaTeXRenderer) == assertions[assertion]
