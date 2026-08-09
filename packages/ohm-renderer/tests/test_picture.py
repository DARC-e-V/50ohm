import pytest
from ohm_renderer.document import Document
from ohm_renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from ohm_renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer


@pytest.mark.html
def test_picture_html():
    assertions = {
        "[picture:0:abc:Text]": '<figure class="picture" id="ref_abc">\n'
        '  <img src="pictures/0.svg" alt="">\n'
        "  <figcaption>Abbildung A-5.7.1: Text</figcaption>\n"
        "</figure>\n",
    }

    with FiftyOhmHtmlRenderer(edition="A", chapter="5", section="7") as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == assertions[assertion]


@pytest.mark.latex
def test_picture_latex():
    assertions = {
        "[picture:0:abc:Text]": FiftyOhmLaTeXRenderer.render_picture_helper("0", "abc", "Text", "TODO"),
    }

    with FiftyOhmLaTeXRenderer() as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == assertions[assertion]
