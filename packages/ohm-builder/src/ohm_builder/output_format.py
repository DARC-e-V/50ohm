from enum import StrEnum

from .builder import Builder
from .html_builder import HtmlBuilder
from .mdx_builder import MdxBuilder


class OutputFormat(StrEnum):
    html = "html"
    mdx = "mdx"


BUILDERS: dict[OutputFormat, type[Builder]] = {
    OutputFormat.html: HtmlBuilder,
    OutputFormat.mdx: MdxBuilder,
}
