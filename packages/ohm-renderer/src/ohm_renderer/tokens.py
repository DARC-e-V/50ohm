"""The set of tokens that make up DARCdown, shared by the renderers."""

from .comment import BlockComment
from .dash import Dash
from .formula import Formula
from .halfwidth_spaces import HalfwidthSpaces
from .image import Image
from .include import Include
from .index import Index
from .morse import Morse
from .nonbreaking_spaces import NonbreakingSpaces, NonbreakingSpacesDots
from .qso import Qso
from .question import Question
from .reference import Reference
from .smartquote import Smartquote
from .table import Table
from .tag import Tag
from .underline import Underline
from .unit import Unit

# Which tokens exist is a property of the language, not of an output format, so every
# renderer that reads DARCdown registers this same list.
DARCDOWN_TOKENS = (
    Dash,
    BlockComment,
    Smartquote,
    Unit,
    Underline,
    Morse,
    Tag,
    HalfwidthSpaces,
    NonbreakingSpaces,
    NonbreakingSpacesDots,
    Reference,
    Question,
    Image,
    Table,
    Qso,
    Include,
    Formula,
    Index,
)
