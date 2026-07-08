import pytest

from renderer.document import Document
from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_html_slide_renderer import FiftyOhmHtmlSlideRenderer


@pytest.mark.html
def test_hierarchical_picture_numbering():
    """Pictures get hierarchical numbers in format edition-chapter.section.counter"""
    markdown_text = """
[picture:123:pic1:First picture]

Some text here.

[picture:456:pic2:Second picture]

Reference to first: [ref:pic1]
Reference to second: [ref:pic2]
"""

    renderer = FiftyOhmHtmlRenderer(edition="E", chapter="2", section="3")
    doc = Document(markdown_text)

    # Counter is assigned in document order during parsing.
    assert doc.references["pic1"] == "1"
    assert doc.references["pic2"] == "2"

    result = renderer.render(doc)

    # Hierarchical numbers in the figure captions.
    assert "Abbildung E-2.3.1:" in result
    assert "Abbildung E-2.3.2:" in result

    # References are resolved to the same numbers.
    assert ">E-2.3.1</a>" in result
    assert ">E-2.3.2</a>" in result


@pytest.mark.html
def test_hierarchical_photo_numbering():
    """Photos get hierarchical numbers from the shared counter"""
    markdown_text = """
[photo:789:photo1:First photo]

[photo:101:photo2:Second photo]

Reference: [ref:photo1]
"""

    renderer = FiftyOhmHtmlRenderer(edition="N", chapter="1", section="2")
    doc = Document(markdown_text)

    assert doc.references["photo1"] == "1"
    assert doc.references["photo2"] == "2"

    result = renderer.render(doc)

    assert "Abbildung N-1.2.1:" in result
    assert "Abbildung N-1.2.2:" in result
    assert ">N-1.2.1</a>" in result


@pytest.mark.html
def test_hierarchical_table_numbering():
    """Tables with names get hierarchical numbers from the shared counter"""
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
    doc = Document(markdown_text)

    assert doc.references["table1"] == "1"
    assert doc.references["table2"] == "2"

    result = renderer.render(doc)

    assert "Tabelle A-3.1.1:" in result
    assert "Tabelle A-3.1.2:" in result
    assert ">A-3.1.1</a>" in result


@pytest.mark.html
def test_mixed_figure_types_share_counter():
    """Pictures, photos, and tables share a single unified counter in document order"""
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
    doc = Document(markdown_text)

    # All types share the same counter, assigned in document order.
    assert doc.references["pic1"] == "1"
    assert doc.references["photo1"] == "2"
    assert doc.references["tab1"] == "3"
    assert doc.references["pic2"] == "4"

    result = renderer.render(doc)

    assert "Abbildung E-5.2.1:" in result  # pic1
    assert "Abbildung E-5.2.2:" in result  # photo1
    assert "Tabelle E-5.2.3:" in result  # tab1
    assert "Abbildung E-5.2.4:" in result  # pic2


@pytest.mark.slide
def test_slide_renderer_adds_s_suffix():
    """The slide renderer adds an 'S' suffix to the edition"""
    markdown_text = """
[picture:1:pic1:Slide picture]

Reference: [ref:pic1]
"""

    renderer = FiftyOhmHtmlSlideRenderer(edition="E", chapter="2", section="1")

    # Edition gains the S suffix.
    assert renderer.edition == "ES"

    result = renderer.render(Document(markdown_text))

    assert "Abbildung ES-2.1.1:" in result
    assert ">ES-2.1.1</a>" in result


@pytest.mark.html
def test_fallback_numbering_without_context():
    """Numbering falls back to a simple counter when context is missing"""
    markdown_text = """
[picture:1:pic1:Picture]

Reference: [ref:pic1]
"""

    # No edition/chapter/section provided.
    renderer = FiftyOhmHtmlRenderer()
    result = renderer.render(Document(markdown_text))

    # Falls back to the bare counter.
    assert "Abbildung 1:" in result
    assert ">1</a>" in result


@pytest.mark.html
def test_unresolved_reference():
    """References to non-existent figures show '?'"""
    markdown_text = """
Reference to non-existent: [ref:nonexistent]
"""

    renderer = FiftyOhmHtmlRenderer(edition="E", chapter="1", section="1")
    result = renderer.render(Document(markdown_text))

    assert ">?</a>" in result


@pytest.mark.html
def test_table_without_name_not_numbered():
    """Tables without names are not numbered and do not consume a counter slot"""
    markdown_text = """
| Header 1 | Header 2 |
| Data 1   | Data 2   |

[picture:1:pic1:Picture one]
"""

    renderer = FiftyOhmHtmlRenderer(edition="E", chapter="1", section="1")
    doc = Document(markdown_text)

    # Only the picture is registered.
    assert doc.references == {"pic1": "1"}

    result = renderer.render(doc)

    assert "Abbildung E-1.1.1:" in result
    assert "Tabelle" not in result
