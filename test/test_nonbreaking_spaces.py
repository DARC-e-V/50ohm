import mistletoe

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from test.util import paragraph

def test_paragraph_html():
    input = "Der Test befindet sich unter §2 vielleicht aber auch § 3."
    target = "Der Test befindet sich unter §&#160;2 vielleicht aber auch §&#160;3."

    assert mistletoe.markdown(input, FiftyOhmHtmlRenderer) == paragraph(target)

def test_three_points_html():
    assertions = {
        "Heute hatte ich ... zum Mittagessen." : "Heute hatte ich&#160;...&#160;zum Mittagessen.",
        "Niemals hätte ich gedacht, dass...ich ...nicht kann." : "Niemals hätte ich gedacht, dass...ich&#160;...nicht kann.",
        "Oh nein ...ein Pinguin." : "Oh nein&#160;...ein Pinguin.",
        "Haha .. . Hahaha" : "Haha .. . Hahaha"
    }

    for key, value in assertions.items():
        assert mistletoe.markdown(key, FiftyOhmHtmlRenderer) == paragraph(value)


def test_absatz_html():
    input = "Der Test befindet sich unter Abs.2 vielleicht aber auch Abs. 3."
    target = "Der Test befindet sich unter Abs.&#160;2 vielleicht aber auch Abs.&#160;3."

    assert mistletoe.markdown(input, FiftyOhmHtmlRenderer) == paragraph(target)

def test_class_html():
    input = "Ich lerne für Klasse A, Klasse E und Klasse N."
    target = "Ich lerne für Klasse&#160;A, Klasse&#160;E und Klasse&#160;N."

    assert mistletoe.markdown(input, FiftyOhmHtmlRenderer) == paragraph(target)


