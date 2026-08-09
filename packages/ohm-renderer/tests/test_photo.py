import pytest
from ohm_renderer.document import Document
from ohm_renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from ohm_renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from util import render_mdx


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


@pytest.mark.mdx
def test_photo_mdx():
    # Without a photo_handler there is no alt text, the figure still renders.
    rendered = render_mdx("[photo:123:abc:Text]", edition="A", chapter="5", section="7")

    assert rendered == (
        '<figure class="photo" id="ref_abc">\n'
        "![](/photos/123.png)\n"
        # The blank line keeps the caption out of the image's paragraph.
        "\n"
        "<figcaption>Abbildung A-5.7.1: Text</figcaption>\n"
        "</figure>\n"
    )


@pytest.mark.latex
def test_photo_latex():
    assertions = {
        "[photo:123:abc:Text]": FiftyOhmLaTeXRenderer.render_photo_helper("123", "abc", "Text", "TODO"),
    }

    with FiftyOhmLaTeXRenderer() as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == assertions[assertion]
