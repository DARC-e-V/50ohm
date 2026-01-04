"""Test that references to figures use hierarchical numbering"""

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_html_slide_renderer import FiftyOhmHtmlSlideRenderer


def test_html_references_with_hierarchical_numbering():
    """Test that references display hierarchical figure numbers"""
    markdown = """
[picture:101:diagram1:First diagram]

Reference to [ref:diagram1].

[photo:201:photo1:First photo]

References: [ref:diagram1] and [ref:photo1].
"""

    with FiftyOhmHtmlRenderer(edition="N", chapter_number=2, section_number=3) as renderer:
        from mistletoe import Document

        result = renderer.render(Document(markdown))

        # Should have figure numbers in captions
        assert "N-2.3.1" in result
        assert "N-2.3.2" in result

        # Should have figure numbers in references (appears 3 times: caption + 2 refs)
        assert result.count("N-2.3.1") == 3  # 1 caption + 2 references
        assert result.count("N-2.3.2") == 2  # 1 caption + 1 reference


def test_html_references_without_context():
    """Test that references work with simple numbering"""
    markdown = """
[picture:101:diagram1:First diagram]

Reference to [ref:diagram1].

[photo:201:photo1:First photo]

References: [ref:diagram1] and [ref:photo1].
"""

    with FiftyOhmHtmlRenderer() as renderer:
        from mistletoe import Document

        result = renderer.render(Document(markdown))

        # Should have simple numbers in captions
        assert "Abbildung 1" in result
        assert "Abbildung 2" in result

        # References should show "1" and "2"
        # Count occurrences in link tags
        import re

        refs = re.findall(r'<a href="[^"]+"\s+onclick="[^"]+">([^<]+)</a>', result)
        assert "1" in refs
        assert "2" in refs
        assert refs.count("1") == 2  # Two references to figure 1
        assert refs.count("2") == 1  # One reference to figure 2


def test_slide_references_with_hierarchical_numbering():
    """Test that slide references display hierarchical figure numbers with S suffix"""
    markdown = """
[picture:101:diagram1:First diagram]

Reference to [ref:diagram1].
"""

    with FiftyOhmHtmlSlideRenderer(edition="NEA", chapter_number=7, section_number=8) as renderer:
        from mistletoe import Document

        result = renderer.render(Document(markdown))

        # Should have NEAS (NEA + S) in both caption and reference
        assert result.count("NEAS-7.8.1") == 2  # 1 caption + 1 reference


def test_reference_to_nonexistent_figure():
    """Test that references to non-existent figures show '?'"""
    markdown = """
[picture:101:diagram1:First diagram]

Reference to [ref:nonexistent].
"""

    with FiftyOhmHtmlRenderer(edition="N", chapter_number=1, section_number=1) as renderer:
        from mistletoe import Document

        result = renderer.render(Document(markdown))

        # Should have the figure number
        assert "N-1.1.1" in result

        # Reference to non-existent figure should show "?"
        import re

        refs = re.findall(r'<a href="[^"]+"\s+onclick="[^"]+">([^<]+)</a>', result)
        assert "?" in refs


def test_reference_before_figure():
    """Test that references work even when they appear before the figure definition"""
    markdown = """
Reference to [ref:diagram1] appears first.

[picture:101:diagram1:First diagram]

Another reference to [ref:diagram1].
"""

    with FiftyOhmHtmlRenderer(edition="N", chapter_number=2, section_number=3) as renderer:
        from mistletoe import Document

        result = renderer.render(Document(markdown))

        # Both references should show the correct figure number
        import re

        refs = re.findall(r'<a href="[^"]+"\s+onclick="[^"]+">([^<]+)</a>', result)
        assert len(refs) == 2
        assert all(ref == "N-2.3.1" for ref in refs)
        assert "?" not in refs
