import pytest
from mistletoe.markdown_renderer import MarkdownRenderer
from ohm_renderer.document import Document
from ohm_renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from ohm_renderer.table import Table
from util import render_html


@pytest.mark.html
def test_table_html():
    assertions = {
        "| l: a |": '<table class="table table-hover">\n<thead>\n<tr>\n<th style="text-align: left;">a</th>\n</tr>\n</thead>\n</table>\n',  # noqa: E501
        "| r: a |": '<table class="table table-hover">\n<thead>\n<tr>\n<th style="text-align: right;">a</th>\n</tr>\n</thead>\n</table>\n',  # noqa: E501
        "| c: a |": '<table class="table table-hover">\n<thead>\n<tr>\n<th style="text-align: center;">a</th>\n</tr>\n</thead>\n</table>\n',  # noqa: E501
        "| l: a |\n| b |": '<table class="table table-hover">\n<thead>\n<tr>\n<th style="text-align: left;">a</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td style="text-align: left;">b</td>\n</tr>\n</tbody>\n</table>\n',  # noqa: E501
        "| l: a |\n| b |\n| c |": '<table class="table table-hover">\n<thead>\n<tr>\n<th style="text-align: left;">a</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td style="text-align: left;">b</td>\n</tr>\n<tr>\n<td style="text-align: left;">c</td>\n</tr>\n</tbody>\n</table>\n',  # noqa: E501
        "| a |\n| b |\n| c |": '<table class="table table-hover">\n<thead>\n<tr>\n<th>a</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td>b</td>\n</tr>\n<tr>\n<td>c</td>\n</tr>\n</tbody>\n</table>\n',  # noqa: E501
        "| l: a |\n| *b* |": '<table class="table table-hover">\n<thead>\n<tr>\n<th style="text-align: left;">a</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td style="text-align: left;"><em>b</em></td>\n</tr>\n</tbody>\n</table>\n',  # noqa: E501
        "| l: a |\n| b |\n[table:n_ab:A und B]": '<table class="table table-hover" id="ref_n_ab" name="n_ab">\n<caption>Tabelle 1: A und B</caption>\n<thead>\n<tr>\n<th style="text-align: left;">a</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td style="text-align: left;">b</td>\n</tr>\n</tbody>\n</table>\n',  # noqa: E501
        # The caption is recognised no matter how the line is indented.
        "| l: a |\n| b |\n  [table:t:C]": '<table class="table table-hover" id="ref_t" name="t">\n<caption>Tabelle 1: C</caption>\n<thead>\n<tr>\n<th style="text-align: left;">a</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td style="text-align: left;">b</td>\n</tr>\n</tbody>\n</table>\n',  # noqa: E501
        "| l: *a* |": '<table class="table table-hover">\n<thead>\n<tr>\n<th style="text-align: left;"><em>a</em></th>\n</tr>\n</thead>\n</table>\n',  # noqa: E501
        "| l: a |\n| [morse:a] |": '<table class="table table-hover">\n<thead>\n<tr>\n<th style="text-align: left;">a</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td style="text-align: left;"><span class="morse"><span class="morse_char">\n<span class="morse_symbol">\n▄</span>\n<span class="morse_symbol">\n▄▄▄</span>\n</span>\n</span></td>\n</tr>\n</tbody>\n</table>\n',  # noqa: E501
        "| l: abc | r: abc | X: abc |\n| 123 | 456 | 789 | \n | 987 | 654 | 321 | ": '<table class="table table-hover">\n<thead>\n<tr>\n<th style="text-align: left;">abc</th>\n<th style="text-align: right;">abc</th>\n<th>abc</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td style="text-align: left;">123</td>\n<td style="text-align: right;">456</td>\n<td>789</td>\n</tr>\n<tr>\n<td style="text-align: left;">987</td>\n<td style="text-align: right;">654</td>\n<td>321</td>\n</tr>\n</tbody>\n</table>\n',  # noqa: E501
        # The header defines the column count, so surplus cells of a row are dropped.
        "| l: a |\n| b | c |": '<table class="table table-hover">\n<thead>\n<tr>\n<th style="text-align: left;">a</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td style="text-align: left;">b</td>\n</tr>\n</tbody>\n</table>\n',  # noqa: E501
        # An empty cell keeps its column, so the following cells stay where they belong.
        "| l: a | c: b | r: c |\n| 1 || 3 |": '<table class="table table-hover">\n<thead>\n<tr>\n<th style="text-align: left;">a</th>\n<th style="text-align: center;">b</th>\n<th style="text-align: right;">c</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td style="text-align: left;">1</td>\n<td style="text-align: center;"></td>\n<td style="text-align: right;">3</td>\n</tr>\n</tbody>\n</table>\n',  # noqa: E501
        # A header without a cell still spans a single column.
        "|\n| b |": '<table class="table table-hover">\n<thead>\n<tr>\n<th></th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td>b</td>\n</tr>\n</tbody>\n</table>\n',  # noqa: E501
        # DARCdown has no GFM tables, such a block stays a paragraph.
        "a | b\n--- | ---\nc | d": "<p>a | b\n--- | ---\nc | d</p>\n",
        # A table interrupts a paragraph, any other line continues it.
        "vorher\n| l: a |": '<p>vorher</p>\n<table class="table table-hover">\n<thead>\n<tr>\n<th style="text-align: left;">a</th>\n</tr>\n</thead>\n</table>\n',  # noqa: E501
        "erste\nzweite": "<p>erste\nzweite</p>\n",
    }

    for assertion in assertions:
        assert render_html(assertion) == assertions[assertion]


@pytest.mark.latex
def test_table_latex():
    assertions = {
        "| l: a |": "\\begin{DARCtabular}{l}\na\\\\\n\\end{DARCtabular}",
        "| l: a |\n| *b* |": "\\begin{DARCtabular}{l}\na\\\\\n\\emph{b}\\\\\n\\end{DARCtabular}",
        "| l: a | X: b |\n| c | d |": "\\begin{DARCtabular}{lX}\na & b\\\\\nc & d\\\\\n\\end{DARCtabular}",
        # Columns without an alignment prefix are typeset left aligned.
        "| a |\n| b |": "\\begin{DARCtabular}{l}\na\\\\\nb\\\\\n\\end{DARCtabular}",
        # A row with fewer cells than the header is padded, so the column count matches.
        "| a | X: b |\n| c |": "\\begin{DARCtabular}{lX}\na & b\\\\\nc & \\\\\n\\end{DARCtabular}",
        # A row with more cells than the header is truncated, so the preamble still fits.
        "| l: a |\n| b | c |": "\\begin{DARCtabular}{l}\na\\\\\nb\\\\\n\\end{DARCtabular}",
        # An empty cell keeps its column, so the following cells stay where they belong.
        "| l: a | c: b | r: c |\n| 1 || 3 |": "\\begin{DARCtabular}{lcr}\na & b & c\\\\\n1 &  & 3\\\\\n\\end{DARCtabular}",  # noqa: E501
        # A header without a cell still spans a single column, never an empty preamble.
        "|\n| b |": "\\begin{DARCtabular}{l}\n\\\\\nb\\\\\n\\end{DARCtabular}",
        # A named table is captioned and labelled below the tabular.
        "| l: a |\n| b |\n[table:n_ab:A und B]": "\\begin{DARCtabular}{l}\na\\\\\nb\\\\\n\\end{DARCtabular}\\captionof{figure}{A und B}\n\\label{n_ab}\n",  # noqa: E501
        # DARCdown has no GFM tables, such a block stays a paragraph.
        "a | b\n--- | ---\nc | d": "\na | b\n--- | ---\nc | d\n",
    }

    with FiftyOhmLaTeXRenderer() as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == assertions[assertion]


@pytest.mark.markdown
def test_table_markdown():
    # Mistletoe's MarkdownRenderer only knows GFM tables, so the roundtrip drops the
    # name, the caption and the alignment prefixes.
    assertions = {
        "| l: a | r: b |\n| c | d |\n[table:n_ab:A und B]": "| a   |   b |\n| --- | --: |\n| c   |   d |\n",
        "| a |": "| a   |\n| --- |\n",
        "| l: a |\n| *b* |": "| a   |\n| --- |\n| *b* |\n",
        "| c: abc | r: abc |\n| 1 | 2 |": "| abc | abc |\n| :-: | --: |\n|  1  |   2 |\n",
        # The expanding column has no markdown counterpart and stays unaligned.
        "| X: abc |\n| 1 |": "| abc |\n| --- |\n| 1   |\n",
    }

    with MarkdownRenderer(Table) as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == assertions[assertion]
