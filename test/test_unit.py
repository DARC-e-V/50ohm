import mistletoe
import pytest

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer

from .util import paragraph


@pytest.mark.html
def test_basic_units_html():
    """Test basic units: Insert non-breaking, smaller space."""
    assertions = {
        "1 V": "1&#8239;V",
        "0,12 V": "0,12&#8239;V",
        "0,75 kW": "0,75&#8239;kW",
        "33 A": "33&#8239;A",
        "1 Ah": "1&#8239;Ah",  # Ah can be a tricky case if the RegEx is wrong, as A might match before Ah, thus rendering the output with an "A" unit
        "10 A/mm²": "10&#8239;A/mm²",
        "DL9MJ": "DL9MJ",  # Ensure other strings, like callsings, aren‘t mistaken for units. ;)
        "Ein Satz mit 200 V.": "Ein Satz mit 200&#8239;V.",  # Support units before sentence ends.
    }

    for input, output in assertions.items():
        assert mistletoe.markdown(input, FiftyOhmHtmlRenderer) == paragraph(output)


@pytest.mark.html
def test_translated_units_html():
    """Test translated units: Replace Ohm with Ω."""
    assertions = {
        "50 Ohm": "50&#8239;Ω",
        "100 mOhm": "100&#8239;mΩ",
    }

    for input, output in assertions.items():
        assert mistletoe.markdown(input, FiftyOhmHtmlRenderer) == paragraph(output)


@pytest.mark.html
def test_special_units_html():
    """Test special units: Don't put space before ° and %."""
    assertions = {
        "100%": "100%",
        "100 %": "100%",
        "42,24°": "42,24°",
    }

    for input, output in assertions.items():
        assert mistletoe.markdown(input, FiftyOhmHtmlRenderer) == paragraph(output)
