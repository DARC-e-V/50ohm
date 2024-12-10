import mistletoe

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer


def test_morse_html() :

    assertions = {
        '"[morse:a]"' : "<p>"+FiftyOhmHtmlRenderer.render_morse_helper([[1,2]])+"</p>\n",
        '"[morse: a]"' : "<p>"+FiftyOhmHtmlRenderer.render_morse_helper([[1,2]])+"</p>\n",
        '"[morse: aaa]"' : "<p>"+FiftyOhmHtmlRenderer.render_morse_helper([[1,2],[1,2],[1,2]])+"</p>\n",
        '"[morse: a a]"' : "<p>"+FiftyOhmHtmlRenderer.render_morse_helper([[1,2],[3],[1,2]])+"</p>\n",
        '"[morse: db0]"' : "<p>"+FiftyOhmHtmlRenderer.render_morse_helper([[2,1,1],[2,1,1,1],[2,2,2,2,2]])+"</p>\n",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == assertions[assertion]