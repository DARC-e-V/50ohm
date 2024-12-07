import mistletoe

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from test.util import paragraph

def test_paragraph_html():
    input = "Der Test befindet sich unter §2 vielleicht aber auch § 3."
    target = "Der Test befindet sich unter §&#160;2 vielleicht aber auch §&#160;3."

    assert mistletoe.markdown(input, FiftyOhmHtmlRenderer) == paragraph(target)

def test_three_points_html():
    input = "Heute hatte ich ... zum Mittagessen."
    target = "Heute hatte ich&#160;...&#160;zum Mittagessen."

    assert mistletoe.markdown(input, FiftyOhmHtmlRenderer) == paragraph(target)


def test_absatz_html():
    input = "Der Test befindet sich unter Abs.2 vielleicht aber auch Abs. 3."
    target = "Der Test befindet sich unter Abs.&#160;2 vielleicht aber auch Abs.&#160;3."

    assert mistletoe.markdown(input, FiftyOhmHtmlRenderer) == paragraph(target)

def test_class_html():
    input = "Ich lerne für Klasse A, Klasse E und Klasse N."
    target = "Ich lerne für Klasse&#160;A, Klasse&#160;E und Klasse&#160;N."

    assert mistletoe.markdown(input, FiftyOhmHtmlRenderer) == paragraph(target)


