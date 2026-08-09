import pytest
from ohm_renderer.fifty_ohm_mdx_renderer import NARROW_NBSP

from .util import paragraph, render_html, render_mdx


@pytest.mark.html
def test_basic_units_html():
    """Test basic units: Insert non-breaking, smaller space."""
    assertions = {
        "1 V": "1&#8239;V",
        "0,12 V": "0,12&#8239;V",
        "0,75 kW": "0,75&#8239;kW",
        "33 A": "33&#8239;A",
        "1 Ah": "1&#8239;Ah",
        "10 A/mm²": "10&#8239;A/mm²",
        "DL9MJ": "DL9MJ",  # Ensure other strings, like callsings, aren‘t mistaken for units. ;)
        "Ein Satz mit 200 V.": "Ein Satz mit 200&#8239;V.",  # Support units before sentence ends.
    }

    for input, output in assertions.items():
        assert render_html(input) == paragraph(output)


@pytest.mark.html
def test_translated_units_html():
    """Test translated units: Replace Ohm with Ω."""
    assertions = {
        "50 Ohm": "50&#8239;Ω",
        "100 mOhm": "100&#8239;mΩ",
    }

    for input, output in assertions.items():
        assert render_html(input) == paragraph(output)


@pytest.mark.html
def test_special_units_html():
    """Test special units: Don't put space before ° and %."""
    assertions = {
        "100%": "100%",
        "100 %": "100%",
        "42,24°": "42,24°",
    }

    for input, output in assertions.items():
        assert render_html(input) == paragraph(output)


@pytest.mark.mdx
def test_units_mdx():
    """The entities of the HTML renderer become literal characters in Markdown."""
    assertions = {
        "1 V": f"1{NARROW_NBSP}V\n",
        "0,75 kW": f"0,75{NARROW_NBSP}kW\n",
        "10 A/mm²": f"10{NARROW_NBSP}A/mm²\n",
        "DL9MJ": "DL9MJ\n",
        "50 Ohm": f"50{NARROW_NBSP}Ω\n",
        "100 mOhm": f"100{NARROW_NBSP}mΩ\n",
        # No space before ° and %.
        "100 %": "100%\n",
        "42,24°": "42,24°\n",
    }

    for input, output in assertions.items():
        assert render_mdx(input) == output
