import pytest
from util import render_html, render_mdx


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


@pytest.mark.mdx
def test_formula_mdx():
    # A fence is the only spelling remark-math reads as display math, "$$…$$" on a single
    # line stays inline math.
    fence = "$$\n" + r"a \cdot b" + "\n$$\n"
    assertions = {
        r"$a \cdot b$": fence,
        r" $a \cdot b$ ": fence,
        r"$ a \cdot b $": fence,
        r"$a \cdot b$" + "\n" + r"$a \cdot b$": fence + fence,
        # A fence interrupts a paragraph in MDX, so no blank line is needed before it.
        "Lorem Ipsum\n" + r"$a \cdot b$": "Lorem Ipsum\n" + fence,
        # Inline formulas are untouched, remark-math protects their braces in MDX.
        r"Es gilt $\qty{1}{\volt}$ hier.": "Es gilt " + r"$\qty{1}{\volt}$" + " hier.\n",
    }

    for assertion in assertions:
        assert render_mdx(assertion) == assertions[assertion]
