from enum import Enum, auto


class PathStyle(Enum):
    # Line with Start end endpoint
    LINE = auto()
    # Line wit only endpoint
    LINE_NOMOVE = auto()
    # Quarter circle with move to first point
    QUARTERCIRCLE = auto()
    # Quarter circle to point from current location
    QUARTERCIRCLE_NOMOVE = auto()
    HALFCIRCLE = auto()
    HALFCIRCLE_NOMOVE = auto()

    THUMBHOLE = auto()
    PAIR = auto()
    LINEPLAIN = auto()
    LINEPLAINMOVE = auto()
    LINEPLAINNOMOVE = auto()


