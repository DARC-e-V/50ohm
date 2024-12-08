import mistletoe

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer

from .util import paragraph


def test_unit_html():
    assertions = {
        "0,1 V": "0,1&#8239;V",
        "33 A": "33&#8239;A",
        "1 Ah": "1&#8239;Ah",
        "100 mOhm": "100&#8239;mΩ",
        "25 Ohm": "25&#8239;Ω",
    }

    for input, output in assertions.items():
        assert mistletoe.markdown(input, FiftyOhmHtmlRenderer) == paragraph(output)
