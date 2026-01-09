import mistletoe
import pytest

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_html_slide_renderer import FiftyOhmHtmlSlideRenderer


@pytest.mark.html
def test_hierarchical_picture_numbering():
    """Test that pictures get hierarchical numbers in format edition-chapter.section.counter"""
    markdown_text = """
[picture:123:pic1:First picture]

Some text here.

[picture:456:pic2:Second picture]

Reference to first: [ref:pic1]
Reference to second: [ref:pic2]
"""

    renderer = FiftyOhmHtmlRenderer(edition="E", chapter="2", section="3")
    doc = mistletoe.Document(markdown_text)

    # First pass: collect figures
    renderer.collect_figures(doc)

    # Verify figure map
    assert renderer.figure_map["pic1"] == "E-2.3.1"
    assert renderer.figure_map["pic2"] == "E-2.3.2"

    # Second pass: render
    result = renderer.render(doc)

    # Verify hierarchical numbers in output
    assert "Abbildung E-2.3.1:" in result
    assert "Abbildung E-2.3.2:" in result

    # Verify references are resolved
    assert ">E-2.3.1</a>" in result
    assert ">E-2.3.2</a>" in result


@pytest.mark.html
def test_hierarchical_photo_numbering():
    """Test that photos get hierarchical numbers"""
    markdown_text = """
[photo:789:photo1:First photo]

[photo:101:photo2:Second photo]

Reference: [ref:photo1]
"""

    renderer = FiftyOhmHtmlRenderer(edition="N", chapter="1", section="2")
    doc = mistletoe.Document(markdown_text)

    renderer.collect_figures(doc)

    assert renderer.figure_map["photo1"] == "N-1.2.1"
    assert renderer.figure_map["photo2"] == "N-1.2.2"

    result = renderer.render(doc)

    assert "Abbildung N-1.2.1:" in result
    assert "Abbildung N-1.2.2:" in result
    assert ">N-1.2.1</a>" in result


@pytest.mark.html
def test_hierarchical_table_numbering():
    """Test that tables with names get hierarchical numbers"""
    markdown_text = """
| Header 1 | Header 2 |
| Data 1   | Data 2   |
[table:table1:First table]

| Col A | Col B |
| Val 1 | Val 2 |
[table:table2:Second table]

Reference: [ref:table1]
"""

    renderer = FiftyOhmHtmlRenderer(edition="A", chapter="3", section="1")
    doc = mistletoe.Document(markdown_text)

    renderer.collect_figures(doc)

    assert renderer.figure_map["table1"] == "A-3.1.1"
    assert renderer.figure_map["table2"] == "A-3.1.2"

    result = renderer.render(doc)

    assert "Tabelle A-3.1.1:" in result
    assert "Tabelle A-3.1.2:" in result
    assert ">A-3.1.1</a>" in result


@pytest.mark.html
def test_mixed_figure_types_share_counter():
    """Test that pictures, photos, and tables share a single unified counter"""
    markdown_text = """
[picture:1:pic1:Picture one]

[photo:2:photo1:Photo one]

| A | B |
| 1 | 2 |
[table:tab1:Table one]

[picture:3:pic2:Picture two]

References: [ref:pic1], [ref:photo1], [ref:tab1], [ref:pic2]
"""

    renderer = FiftyOhmHtmlRenderer(edition="E", chapter="5", section="2")
    doc = mistletoe.Document(markdown_text)

    renderer.collect_figures(doc)

    # All types share the same counter
    assert renderer.figure_map["pic1"] == "E-5.2.1"
    assert renderer.figure_map["photo1"] == "E-5.2.2"
    assert renderer.figure_map["tab1"] == "E-5.2.3"
    assert renderer.figure_map["pic2"] == "E-5.2.4"

    result = renderer.render(doc)

    # Verify all references are resolved with correct numbers
    assert "Abbildung E-5.2.1:" in result  # pic1
    assert "Abbildung E-5.2.2:" in result  # photo1
    assert "Tabelle E-5.2.3:" in result  # tab1
    assert "Abbildung E-5.2.4:" in result  # pic2


@pytest.mark.slide
def test_slide_renderer_adds_s_suffix():
    """Test that slide renderer adds 'S' suffix to edition"""
    markdown_text = """
[picture:1:pic1:Slide picture]

Reference: [ref:pic1]
"""

    renderer = FiftyOhmHtmlSlideRenderer(edition="E", chapter="2", section="1")
    doc = mistletoe.Document(markdown_text)

    # Verify edition has S suffix
    assert renderer.edition == "ES"

    renderer.collect_figures(doc)

    # Verify hierarchical number includes S
    assert renderer.figure_map["pic1"] == "ES-2.1.1"

    result = renderer.render(doc)

    assert "Abbildung ES-2.1.1:" in result
    assert ">ES-2.1.1</a>" in result


@pytest.mark.html
def test_fallback_numbering_without_context():
    """Test that numbering falls back to simple counter when context is missing"""
    markdown_text = """
[picture:1:pic1:Picture]

Reference: [ref:pic1]
"""

    # No edition/chapter/section provided
    renderer = FiftyOhmHtmlRenderer()
    doc = mistletoe.Document(markdown_text)

    renderer.collect_figures(doc)

    # Should fall back to simple counter
    assert renderer.figure_map["pic1"] == "1"

    result = renderer.render(doc)

    assert "Abbildung 1:" in result
    assert ">1</a>" in result


@pytest.mark.html
def test_unresolved_reference():
    """Test that references to non-existent figures show '?'"""
    markdown_text = """
Reference to non-existent: [ref:nonexistent]
"""

    renderer = FiftyOhmHtmlRenderer(edition="E", chapter="1", section="1")
    doc = mistletoe.Document(markdown_text)

    renderer.collect_figures(doc)

    result = renderer.render(doc)

    # Should show ? for unresolved reference
    assert ">?</a>" in result


@pytest.mark.html
def test_table_without_name_not_numbered():
    """Test that tables without names are not numbered"""
    markdown_text = """
| Header 1 | Header 2 |
| Data 1   | Data 2   |

[picture:1:pic1:Picture one]
"""

    renderer = FiftyOhmHtmlRenderer(edition="E", chapter="1", section="1")
    doc = mistletoe.Document(markdown_text)

    renderer.collect_figures(doc)

    # Only the picture should be numbered
    assert renderer.figure_map["pic1"] == "E-1.1.1"
    assert renderer.figure_counter == 1
