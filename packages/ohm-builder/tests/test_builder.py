import pytest
from ohm_builder.builder import Builder
from ohm_builder.html_builder import HtmlBuilder
from ohm_builder.mdx_builder import MdxBuilder

# Every hook is abstract on purpose, so that a new output format has to make a conscious
# decision about each piece of content instead of silently inheriting a no-op.
HOOKS = {
    "_write_edition_index",
    "_write_chapter_index",
    "_render_section",
    "_write_section",
    "_render_slide",
    "_write_slidedeck",
    "build_website",
    "build_solutions",
    "build_assets",
    "_index_output_dir",
}


@pytest.mark.builder
def test_every_hook_is_abstract():
    assert Builder.__abstractmethods__ == frozenset(HOOKS)


@pytest.mark.builder
@pytest.mark.parametrize("builder", [HtmlBuilder, MdxBuilder])
def test_builders_implement_every_hook(builder):
    assert builder.__abstractmethods__ == frozenset()


@pytest.mark.builder
@pytest.mark.parametrize("skipped", sorted(HOOKS))
def test_a_builder_cannot_leave_a_hook_out(skipped):
    namespace = {hook: (lambda self, *args: None) for hook in HOOKS - {skipped}}
    incomplete = type("Incomplete", (Builder,), namespace)

    with pytest.raises(TypeError, match=skipped):
        incomplete(None)
