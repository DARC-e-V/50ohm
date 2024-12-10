import mistletoe

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from test.util import paragraph


def test_halfwidth_space_html():
    assertions = {
        "Dies ist z.B. ein Test. D.h. hier sollten d.h. Spaces ersetzt worden sein." : "Dies ist z.&#8239;B. ein Test. D.&#8239;h. hier sollten d.&#8239;h. Spaces ersetzt worden sein.",
        "Dies ist z. B. ein Test. D. h. hier sollten d. h. Spaces ersetzt worden sein." : "Dies ist z.&#8239;B. ein Test. D.&#8239;h. hier sollten d.&#8239;h. Spaces ersetzt worden sein.",
        "Z. B. die D.B. wird auch ersetzt, aber das macht nix." : "Z.&#8239;B. die D.&#8239;B. wird auch ersetzt, aber das macht nix."
    }
    
    for key, value in assertions.items():
        assert mistletoe.markdown(key, FiftyOhmHtmlRenderer) == paragraph(value)
