from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class Cell:
    """A simple cell"""
    mine: bool = False
    flagged: bool = False
    covered: bool = True
    mine_count: int = 0

@dataclass
class Board:
    """A board containing cells"""
    cols: int
    rows: int
    mines: int
    cells: list[list[Cell]] = field(init=False)

    def __post_init__(self):
        pass

    def initmines(self, start):
        pass

    def uncover(self, pos):
        pass
    
    def flag(self, pos):
        pass

    def unflag(self, pos):
        pass

class Minesweeper:
    pass
