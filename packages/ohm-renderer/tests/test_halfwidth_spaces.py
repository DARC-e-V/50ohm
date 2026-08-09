import mistletoe
import pytest
from ohm_renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from ohm_renderer.fifty_ohm_mdx_renderer import NARROW_NBSP
from util import paragraph, render_html, render_mdx


@pytest.mark.html
def test_halfwidth_space_html():
    input = "Dies ist z.B. ein Test. D.h. hier sollten d.h. Spaces ersetzt worden sein."
    target = "Dies ist z.&#8239;B. ein Test. D.&#8239;h. hier sollten d.&#8239;h. Spaces ersetzt worden sein."

    assert render_html(input) == paragraph(target)


@pytest.mark.mdx
def test_halfwidth_space_mdx():
    """The &#8239; of the HTML renderer becomes a literal narrow no-break space."""
    input = "Dies ist z.B. ein Test. D.h. hier sollten d.h. Spaces ersetzt worden sein."
    target = (
        f"Dies ist z.{NARROW_NBSP}B. ein Test. "
        f"D.{NARROW_NBSP}h. hier sollten d.{NARROW_NBSP}h. Spaces ersetzt worden sein.\n"
    )

    assert render_mdx(input) == target


@pytest.mark.latex
def test_halfwidth_space_latex():
    input = "Dies ist z.B. ein Test. D.h. hier sollten d.h. Spaces ersetzt worden sein."
    target = "\nDies ist z.\\,B. ein Test. D.\\,h. hier sollten d.\\,h. Spaces ersetzt worden sein.\n"

    assert mistletoe.markdown(input, FiftyOhmLaTeXRenderer) == target
