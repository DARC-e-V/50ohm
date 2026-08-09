import mistletoe
import pytest
from ohm_renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from util import paragraph, render_html, render_mdx


@pytest.mark.html
def test_comment_html():
    assertions = {
        "%Comment\nBar": paragraph("Bar"),
        "%Comment\n": "",
        "Foo 100 % Bar": paragraph("Foo 100% Bar"),
        "Foo\n%Comment\nBar": paragraph("Foo") + paragraph("Bar"),
    }

    for assertion in assertions:
        assert render_html(assertion) == assertions[assertion]


@pytest.mark.mdx
def test_comment_mdx():
    assertions = {
        "%Comment\nBar": "Bar\n",
        "%Comment\n": "",
        "Foo 100 % Bar": "Foo 100% Bar\n",
        # The comment separated two paragraphs, so it leaves a blank line behind.
        "Foo\n%Comment\nBar": "Foo\n\nBar\n",
        # Where the source already had blank lines, that leaves extra ones. Harmless.
        "Foo\n\n%Comment\n\nBar": "Foo\n\n\n\nBar\n",
    }

    for assertion in assertions:
        assert render_mdx(assertion) == assertions[assertion]


@pytest.mark.latex
def test_comment_latex():
    assertions = {
        "%Comment\nBar": "% Comment\n\nBar\n",
        "%Comment\n": "% Comment\n",
        "Foo 100 % Bar": "\nFoo 100 \\% Bar\n",
        "Foo\n%Comment\nBar": "\nFoo\n% Comment\n\nBar\n",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmLaTeXRenderer) == assertions[assertion]
