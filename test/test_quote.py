import mistletoe

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from test.util import paragraph


def test_quote_html() :

    assertions = {
        '"quote"'  : '„quote“',
        '" quote "' : '„ quote “',
        '"quote" "' : '„quote“ "',
        '"quo te1" filltext "qu ot e2"' : '„quo te1“ filltext „qu ot e2“',
        '"quo *te1*" filltext "qu ot e2"' : '„quo <em>te1</em>“ filltext „qu ot e2“',
        '""' : '""',
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == paragraph(assertions[assertion])
