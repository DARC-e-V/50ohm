from enum import Enum


class Edition(str, Enum):
    n = "N"
    e = "E"
    a = "A"
    ne = "NE"
    ea = "EA"
    nea = "NEA"
