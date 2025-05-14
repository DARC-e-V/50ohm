import pytest
from mistletoe import Document

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer


@pytest.mark.html
def test_table_html():
    assertions = {
        "| l: a |" : "<table><tr><th style='text-align: left;'>a</th></tr></table>\n",
        "| r: a |" : "<table><tr><th style='text-align: right;'>a</th></tr></table>\n",
        "| l: a |\n| *b* |" : "<table><tr><th style='text-align: left;'>a</th></tr><tr><td style='text-align: left;'><em>b</em></td></tr></table>\n",
        "| l: *a* |" : "<table><tr><th style='text-align: left;'><em>a</em></th></tr></table>\n",
        "| l: a |\n| [morse:a] |" : "<table><tr><th style=\'text-align: left;\'>a</th></tr><tr><td style=\'text-align: left;\'><span class=\"morse\"><span class=\"morse_char\">\n<span class=\"morse_char\">\n▄</span>\n<span class=\"morse_char\">\n▄▄▄</span>\n</span>\n</span></td></tr></table>\n",
        "| l: a |\n| b |" : "<table><tr><th style='text-align: left;'>a</th></tr><tr><td style='text-align: left;'>b</td></tr></table>\n",
        "| l: abc | r: abc | X: abc |\n| 123 | 456 | 789 | \n | 987 | 654 | 321 | ": "<table><tr><th style='text-align: left;'>abc</th><th style='text-align: right;'>abc</th><th>abc</th></tr><tr><td style='text-align: left;'>123</td><td style='text-align: right;'>456</td><td>789</td></tr><tr><td style='text-align: left;'>987</td><td style='text-align: right;'>654</td><td>321</td></tr></table>\n",
    }

    with FiftyOhmHtmlRenderer() as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == assertions[assertion]


@pytest.mark.latex
def test_thematic_break_latex():
    assertions = {
        "| l: a |" : "\\begin{DARCtabular}{l}\na\\\\\n\\end{DARCtabular}",
        "| l: a |\n| *b* |" : "\\begin{DARCtabular}{l}\na\\\\\n\\emph{b}\\\\\n\\end{DARCtabular}",
        "| l: a | X: b |\n| c | d |" : "\\begin{DARCtabular}{lX}\na & b\\\\\nc & d\\\\\n\\end{DARCtabular}",
    }

    with FiftyOhmLaTeXRenderer() as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == assertions[assertion]
