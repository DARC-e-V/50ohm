import pytest
from ohm_renderer.document import Document
from ohm_renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from ohm_renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer


@pytest.mark.html
def test_photo_html():
    assertions = {
        "[photo:123:abc:Text]": '<figure class="photo" id="ref_abc">\n'
        '  <img src="photos/123.png" alt="">\n'
        "  <figcaption>Abbildung A-5.7.1: Text</figcaption>\n"
        "</figure>\n",
    }

    with FiftyOhmHtmlRenderer(edition="A", chapter="5", section="7") as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == assertions[assertion]


@pytest.mark.latex
def test_photo_latex():
    assertions = {
        "[photo:123:abc:Text]": FiftyOhmLaTeXRenderer.render_photo_helper("123", "abc", "Text", "TODO"),
    }

    with FiftyOhmLaTeXRenderer() as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == assertions[assertion]
