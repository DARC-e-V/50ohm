import mistletoe
import pytest
from ohm_renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from util import paragraph, render_html, render_mdx


@pytest.mark.html
def test_smartquote_html():
    assertions = {
        '"quote"': "„quote“",
        '" quote "': "„ quote “",
        '"quote" "': '„quote“ "',
        '"quo te1" filltext "qu ot e2"': "„quo te1“ filltext „qu ot e2“",
        '"quo *te1*" filltext "qu ot e2"': "„quo <em>te1</em>“ filltext „qu ot e2“",
        '""': '""',
    }

    for assertion in assertions:
        assert render_html(assertion) == paragraph(assertions[assertion])


@pytest.mark.html
def test_blockquote_html():
    # The smart quote token no longer shadows mistletoe's blockquote renderer.
    assert render_html("> zitat") == "<blockquote>\n<p>zitat</p>\n</blockquote>\n"


@pytest.mark.mdx
def test_smartquote_mdx():
    # Straight quotes on purpose, the MDX pipeline does the smart quoting.
    assertions = {
        '"quote"': '"quote"\n',
        '" quote "': '" quote "\n',
        '"quote" "': '"quote" "\n',
        '"quo te1" filltext "qu ot e2"': '"quo te1" filltext "qu ot e2"\n',
        '"quo *te1*" filltext "qu ot e2"': '"quo *te1*" filltext "qu ot e2"\n',
        '""': '""\n',
    }

    for assertion in assertions:
        assert render_mdx(assertion) == assertions[assertion]


@pytest.mark.mdx
def test_blockquote_mdx():
    assert render_mdx("> zitat") == "> zitat\n"


@pytest.mark.latex
def test_smartquote_latex():
    assertions = {
        '"quote"': "\n\\enquote{quote}\n",
        '" quote "': "\n\\enquote{ quote }\n",
        '"quote" "': '\n\\enquote{quote} "\n',
        '"quo te1" filltext "qu ot e2"': "\n\\enquote{quo te1} filltext \\enquote{qu ot e2}\n",
        '"quo *te1*" filltext "qu ot e2"': "\n\\enquote{quo \\emph{te1}} filltext \\enquote{qu ot e2}\n",
        '""': '\n""\n',
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmLaTeXRenderer) == assertions[assertion]


@pytest.mark.latex
def test_blockquote_latex():
    expected = "\\begin{displayquote}\n\nzitat\n\\end{displayquote}\n"
    assert mistletoe.markdown("> zitat", FiftyOhmLaTeXRenderer) == expected
