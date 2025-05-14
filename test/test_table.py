import pytest
from mistletoe import Document

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer


@pytest.mark.html
def test_table_html():
    assertions = {
        "| l: a |": '<table>\n<tr>\n<th style="text-align: left;">a</th>\n</tr>\n</table>\n',
        "| r: a |": '<table>\n<tr>\n<th style="text-align: right;">a</th>\n</tr>\n</table>\n',
        "| c: a |": '<table>\n<tr>\n<th style="text-align: center;">a</th>\n</tr>\n</table>\n',
        "| l: a |\n| b |": '<table>\n<tr>\n<th style="text-align: left;">a</th>\n</tr>\n<tr>\n<td style="text-align: left;">b</td>\n</tr>\n</table>\n',
        "| l: a |\n| b |\n| c |": '<table>\n<tr>\n<th style="text-align: left;">a</th>\n</tr>\n<tr>\n<td style="text-align: left;">b</td>\n</tr>\n<tr>\n<td style="text-align: left;">c</td>\n</tr>\n</table>\n',
        "| a |\n| b |\n| c |": "<table>\n<tr>\n<th>a</th>\n</tr>\n<tr>\n<td>b</td>\n</tr>\n<tr>\n<td>c</td>\n</tr>\n</table>\n",
        "| l: a |\n| *b* |": '<table>\n<tr>\n<th style="text-align: left;">a</th>\n</tr>\n<tr>\n<td style="text-align: left;"><em>b</em></td>\n</tr>\n</table>\n',
        "| l: a |\n| b |\n[table:n_ab:A und B]": '<table>\n<tr>\n<th style="text-align: left;">a</th>\n</tr>\n<tr>\n<td style="text-align: left;">b</td>\n</tr>\n<caption>A und B</caption></table>\n',
        "| l: *a* |": '<table>\n<tr>\n<th style="text-align: left;"><em>a</em></th>\n</tr>\n</table>\n',
        "| l: a |\n| [morse:a] |": '<table>\n<tr>\n<th style="text-align: left;">a</th>\n</tr>\n<tr>\n<td style="text-align: left;"><span class="morse"><span class="morse_char">\n<span class="morse_char">\n▄</span>\n<span class="morse_char">\n▄▄▄</span>\n</span>\n</span></td>\n</tr>\n</table>\n',
        "| l: abc | r: abc | X: abc |\n| 123 | 456 | 789 | \n | 987 | 654 | 321 | ": '<table>\n<tr>\n<th style="text-align: left;">abc</th>\n<th style="text-align: right;">abc</th>\n<th>abc</th>\n</tr>\n<tr>\n<td style="text-align: left;">123</td>\n<td style="text-align: right;">456</td>\n<td>789</td>\n</tr>\n<tr>\n<td style="text-align: left;">987</td>\n<td style="text-align: right;">654</td>\n<td>321</td>\n</tr>\n</table>\n',
    }

    with FiftyOhmHtmlRenderer() as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == assertions[assertion]


@pytest.mark.latex
def test_thematic_break_latex():
    assertions = {
        "| l: a |": "\\begin{DARCtabular}{l}\na\\\\\n\\end{DARCtabular}",
        "| l: a |\n| *b* |": "\\begin{DARCtabular}{l}\na\\\\\n\\emph{b}\\\\\n\\end{DARCtabular}",
        "| l: a | X: b |\n| c | d |": "\\begin{DARCtabular}{lX}\na & b\\\\\nc & d\\\\\n\\end{DARCtabular}",
    }

    with FiftyOhmLaTeXRenderer() as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == assertions[assertion]
