import mistletoe

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer


def test_tag_html() :

    assertions = {
        "<margin>\nFoo\n</margin>" : '<div class="margin"><p>Foo</p></div>\n',
        "<indepth>\nFoo\n</indepth>" : '<div class="indepth"><p>Foo</p></div>\n',
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == assertions[assertion]
