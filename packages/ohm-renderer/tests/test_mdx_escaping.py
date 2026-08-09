"""Renderer level protection against MDX's two extra special characters, < and {."""

import pytest
from util import render_mdx


@pytest.mark.mdx
def test_tag_start_is_escaped():
    assertions = {
        # Without the escape MDX reads "<ENG*" as the start of a JSX tag and fails.
        "Tasten wie *<ENG* oder *ENG>*": "Tasten wie *\\<ENG* oder *ENG>*\n",
        # A "<" that cannot open a tag is left alone, so comparisons survive.
        "a < b und a > b": "a < b und a > b\n",
        "5 < 6": "5 < 6\n",
        # Real HTML spans are their own token and must not be escaped.
        "<u>Text</u> und <br/> und <sub>x</sub>": "<u>Text</u> und <br/> und <sub>x</sub>\n",
    }

    for assertion in assertions:
        assert render_mdx(assertion) == assertions[assertion]


@pytest.mark.mdx
def test_line_starting_with_brace_is_folded():
    # MDX reads a "{" at the start of a line as a JSX expression, which breaks inline
    # formulas spanning two lines. A soft line break is whitespace in Markdown and in
    # TeX alike, so folding the line up is lossless.
    source = "$ a = \\frac{1}{2}\n{3} = c $"

    assert render_mdx(source) == "$ a = \\frac{1}{2} {3} = c $\n"


@pytest.mark.mdx
def test_ordinary_line_break_is_kept():
    assert render_mdx("erste\nzweite") == "erste\nzweite\n"
