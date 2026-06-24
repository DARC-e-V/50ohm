import pytest

from test.util import render_html


@pytest.mark.html
def test_formula_html():
    assertions = {
        r"$a \cdot b$": "\n" + r"$$a \cdot b$$" + "\n\n",
        r" $a \cdot b$ ": "\n" + r"$$a \cdot b$$" + "\n\n",
        r"$ a \cdot b $": "\n" + r"$$ a \cdot b $$" + "\n\n",
        r"$a \cdot b$" + "\n" + r"$a \cdot b$": "\n" + r"$$a \cdot b$$" + "\n\n\n" + r"$$a \cdot b$$" + "\n\n",
        r"Lorem Ipsum" + "\n" + r"$a \cdot b$": "<p>Lorem Ipsum</p>\n\n" + r"$$a \cdot b$$" + "\n\n",
    }

    for assertion in assertions:
        assert render_html(assertion) == assertions[assertion]
