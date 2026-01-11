import mistletoe
import pytest

from renderer.document import Document
from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer


@pytest.mark.html
def test_picture_html():
    assertions = {"[picture:0:abc:Text]": ("0", "abc", "Text", "A-5.7.1", "")}

    with FiftyOhmHtmlRenderer(edition="A", chapter="5", section="7") as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == renderer.render_picture_helper(*assertions[assertion]) + "\n"


@pytest.mark.latex
def test_picture_latex():
    assertions = {
        "[picture:0:abc:Text]": FiftyOhmLaTeXRenderer.render_picture_helper("0", "abc", "Text", "TODO"),
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmLaTeXRenderer) == "\n" + assertions[assertion] + "\n"
