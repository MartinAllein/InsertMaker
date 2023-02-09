from enum import Enum, auto


class Direction(Enum):
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()
    HORIZONTAL = auto()
    VERTICAL = auto()


class Rotation(Enum):
    CCW = 0
    CW = 1

