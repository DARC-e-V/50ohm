import mistletoe

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from test.util import paragraph


def test_morse_html():
    assertions = {
        '"[morse:a]"': FiftyOhmHtmlRenderer.render_morse_helper([[1, 2]]),
        '"[morse: a]"': FiftyOhmHtmlRenderer.render_morse_helper([[1, 2]]),
        '"[morse: aaa]"': FiftyOhmHtmlRenderer.render_morse_helper([[1, 2], [1, 2], [1, 2]]),
        '"[morse: a a]"': FiftyOhmHtmlRenderer.render_morse_helper([[1, 2], [3], [1, 2]]),
        '"[morse: db0]"': FiftyOhmHtmlRenderer.render_morse_helper([[2, 1, 1], [2, 1, 1, 1], [2, 2, 2, 2, 2]]),
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == paragraph(assertions[assertion])
