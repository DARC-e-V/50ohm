import mistletoe
import pytest

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from test.util import paragraph


@pytest.mark.html
def test_quote_html():
    assertions = {
        '"quote"': "„quote“",
        '" quote "': "„ quote “",
        '"quote" "': '„quote“ "',
        '"quo te1" filltext "qu ot e2"': "„quo te1“ filltext „qu ot e2“",
        '"quo *te1*" filltext "qu ot e2"': "„quo <em>te1</em>“ filltext „qu ot e2“",
        '""': '""',
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == paragraph(assertions[assertion])


@pytest.mark.latex
def test_quote_latex():
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
