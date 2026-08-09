import pytest
from ohm_renderer.document import Document
from ohm_renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from ohm_renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from util import render_mdx


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


@pytest.mark.mdx
def test_picture_mdx():
    # The accessibility descriptions come from multi-line .txt files, but an alt text
    # cannot span lines and brackets would terminate it early.
    def alt_text(id):
        return "Ein\n [Alt]-Text  "

    rendered = render_mdx("[picture:0:abc:Text]", picture_handler=alt_text, edition="A", chapter="5", section="7")

    assert rendered == (
        '<figure class="picture" id="ref_abc">\n'
        "![Ein Alt-Text](/pictures/0.svg)\n"
        # The blank line keeps the caption out of the image's paragraph.
        "\n"
        "<figcaption>Abbildung A-5.7.1: Text</figcaption>\n"
        "</figure>\n"
    )


@pytest.mark.mdx
def test_inline_image_mdx():
    # The block token for pictures shares its render_map entry with mistletoe's inline
    # image, which must keep rendering as a plain Markdown image.
    assert render_mdx("![a](b.png)") == "![a](b.png)\n"


@pytest.mark.latex
def test_picture_latex():
    assertions = {
        "[picture:0:abc:Text]": FiftyOhmLaTeXRenderer.render_picture_helper("0", "abc", "Text", "TODO"),
    }

    with FiftyOhmLaTeXRenderer() as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == assertions[assertion]
