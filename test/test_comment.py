import mistletoe

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from test.util import paragraph


def test_comment_html():
    assertions = {
        "%Comment\nBar": "Bar",
        # TODO: This test is not working as expected. The comment should be removed
        # "%Comment\n" : "a",
        "Foo\n%Comment\nBar": "Foo\nBar",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == paragraph(assertions[assertion])


def test_comment_latex():
    assertions = {
        "%Comment\nBar": "\nBar\n",
        # TODO: This test is not working as expected. The comment should be removed
        # "%Comment\n" : "a",
        "Foo\n%Comment\nBar": "\nFoo\nBar\n",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmLaTeXRenderer) == assertions[assertion]
