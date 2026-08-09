import pytest
from ohm_renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from util import paragraph, render_html, render_mdx


@pytest.mark.html
def test_morse_html():
    assertions = {
        "[morse:a]": FiftyOhmHtmlRenderer.render_morse_helper([[1, 2]]),
        "[morse:a] abc [morse:a]": f"{FiftyOhmHtmlRenderer.render_morse_helper([[1, 2]])} abc {FiftyOhmHtmlRenderer.render_morse_helper([[1, 2]])}",  # noqa: E501
        "[morse: a]": FiftyOhmHtmlRenderer.render_morse_helper([[1, 2]]),
        "[morse: aaa]": FiftyOhmHtmlRenderer.render_morse_helper([[1, 2], [1, 2], [1, 2]]),
        "[morse: a a]": FiftyOhmHtmlRenderer.render_morse_helper([[1, 2], [3], [1, 2]]),
        "[morse: db0]": FiftyOhmHtmlRenderer.render_morse_helper([[2, 1, 1], [2, 1, 1, 1], [2, 2, 2, 2, 2]]),
    }

    for assertion in assertions:
        assert render_html(assertion) == paragraph(assertions[assertion])


@pytest.mark.mdx
def test_morse_mdx():
    # The component gets the plain text, the conversion to morse code happens in the frontend.
    assertions = {
        "[morse:a]": '<Morse text="a" />\n',
        "[morse: a]": '<Morse text="a" />\n',
        "[morse: db0]": '<Morse text="db0" />\n',
        "A: [morse:a] B: [morse: b]": 'A: <Morse text="a" /> B: <Morse text="b" />\n',
    }

    for assertion in assertions:
        assert render_mdx(assertion) == assertions[assertion]
