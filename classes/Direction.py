from enum import Enum, auto


class Direction(Enum):
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()
    HORIZONTAL = auto()
    VERTICAL = auto()
    CW = auto()
    CCW = auto()