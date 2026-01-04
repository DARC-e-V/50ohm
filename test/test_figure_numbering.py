"""Test hierarchical figure numbering format: edition-chapter.section.image"""

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_html_slide_renderer import FiftyOhmHtmlSlideRenderer


def test_html_hierarchical_numbering():
    """Test HTML renderer produces edition-chapter.section.image format"""
    markdown = """
[picture:101:ref1:First diagram]
[photo:201:ref2:First photo]
[picture:102:ref3:Second diagram]
"""

    with FiftyOhmHtmlRenderer(edition="N", chapter_number=2, section_number=3) as renderer:
        from mistletoe import Document

        result = renderer.render(Document(markdown))

        # Should have N-2.3.1, N-2.3.2, N-2.3.3
        assert "N-2.3.1" in result
        assert "N-2.3.2" in result
        assert "N-2.3.3" in result


def test_slide_hierarchical_numbering():
    """Test slide renderer produces editionS-chapter.section.image format"""
    markdown = """
[picture:101:ref1:First diagram]
[photo:201:ref2:First photo]
"""

    # Note: slide renderer appends "S" to edition, so "NEA" becomes "NEAS"
    with FiftyOhmHtmlSlideRenderer(edition="NEA", chapter_number=7, section_number=8) as renderer:
        from mistletoe import Document

        result = renderer.render(Document(markdown))

        # Should have NEAS-7.8.1, NEAS-7.8.2 (S was appended to NEA)
        assert "NEAS-7.8.1" in result
        assert "NEAS-7.8.2" in result


def test_fallback_simple_numbering():
    """Test renderers fall back to simple numbering without context"""
    markdown = """
[picture:101:ref1:First diagram]
[photo:201:ref2:First photo]
[picture:102:ref3:Second diagram]
"""

    # HTML without context
    with FiftyOhmHtmlRenderer() as renderer:
        from mistletoe import Document

        result = renderer.render(Document(markdown))
        assert "Abbildung 1" in result
        assert "Abbildung 2" in result
        assert "Abbildung 3" in result


def test_counter_independence():
    """Test that each renderer instance has independent counter"""
    markdown = "[picture:101:ref1:Test diagram]"

    # First renderer
    with FiftyOhmHtmlRenderer(edition="N", chapter_number=1, section_number=1) as renderer1:
        from mistletoe import Document

        result1 = renderer1.render(Document(markdown))
        assert "N-1.1.1" in result1

    # Second renderer should also start at 1
    with FiftyOhmHtmlRenderer(edition="N", chapter_number=1, section_number=2) as renderer2:
        from mistletoe import Document

        result2 = renderer2.render(Document(markdown))
        assert "N-1.2.1" in result2


def test_mixed_picture_and_photo():
    """Test that pictures and photos share the same counter"""
    markdown = """
[picture:101:ref1:First item]
[photo:201:ref2:Second item]
[picture:102:ref3:Third item]
[photo:202:ref4:Fourth item]
"""

    with FiftyOhmHtmlRenderer(edition="A", chapter_number=5, section_number=2) as renderer:
        from mistletoe import Document

        result = renderer.render(Document(markdown))

        # Counter should increment across both types
        assert "A-5.2.1" in result
        assert "A-5.2.2" in result
        assert "A-5.2.3" in result
        assert "A-5.2.4" in result
