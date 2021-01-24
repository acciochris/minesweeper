#!/usr/bin/env python3
"""The python implementation of the minesweeper game"""

from __future__ import annotations
from dataclasses import dataclass, field
import random
import curses
import argparse
import sys


class MineError(Exception):
    pass


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
        """Initialize empty board"""
        for _ in self.cols:
            self.cells.append([Cell() for _ in self.rows])

    def _neighbors(self, pos: tuple[int, int]):
        """Return the neighbors of a cell"""
        x, y = pos
        neighbors = (
            (x - 1, y - 1),
            (x, y - 1),
            (x + 1, y - 1),
            (x - 1, y),
            (x + 1, y),
            (x - 1, y + 1),
            (x, y + 1),
            (x + 1, y + 1),
        )
        return {(a, b): self.cells[a][b] for a, b in neighbors}

    def _flag_count(self, pos: tuple[int, int]):
        """Count the flags around a cell"""
        x, y = pos
        count = 0
        for neighbor in self._neighbors((x, y)).values():
            if neighbor.flagged:
                count += 1

        return count

    def _uncover(self, pos: tuple[int, int]):
        """Uncover a single mine"""
        x, y = pos
        if self.cells[x][y].mine:
            raise MineError(pos)
        else:
            self.cells[x][y].covered = False

    def initmines(self, start: tuple[int, int]):
        """Initialize mines with no mine at `start`"""
        # Initialize mines
        poses = [(x, y) for x in self.cols for y in self.rows]
        mines = random.sample([pos for pos in poses if pos != start], self.mines)

        for x, y in mines:
            self.cells[x][y].mine = True

        # Calculate Cell.mine_count
        for x, y in poses:
            cell = self.cells[x][y]
            for neighbor in self._neighbors((x, y)).values():
                if neighbor.mine:
                    cell.mine_count += 1

    def uncover(self, pos: tuple[int, int]):
        """Uncover a cell"""
        x, y = pos
        cell = self.cells[x][y]
        uncovered = []

        # Return if mine count doesn't match flag count
        if cell.mine_count != self._flag_count(pos):
            return []

        # Uncover the cell itself
        if cell.covered:
            self._uncover(pos)
        uncovered.append(pos)

        # Uncover neighbors recursively
        for n_pos, n in self._neighbors(pos).items():
            if n.covered and (not n.flagged):
                self._uncover(n_pos)
                uncovered.append(n_pos)
            if n.mine_count == 0 and (not n.mine):
                for nn_pos in self._neighbors(n_pos).keys():
                    uncovered.extend(self.uncover(nn_pos))

        return uncovered

    def flag(self, pos: tuple[int, int]):
        """Mark a cell as flagged"""
        x, y = pos
        self.cells[x][y].flagged = True

    def unflag(self, pos: tuple[int, int]):
        """Unflag a cell"""
        x, y = pos
        self.cells[x][y].flagged = False


class Minesweeper:
    """UI for the Minesweeper game"""

    def main(self, columns: int, rows: int, mines: int):
        pass


def main(args=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-c",
        "--columns",
        default=9,
        type=int,
        help="The number of columns on the board",
    )
    parser.add_argument(
        "-r",
        "--rows",
        default=9,
        type=int,
        help="The number of rows on the board",
    )
    parser.add_argument(
        "-m",
        "--mines",
        default=10,
        type=int,
        help="The number of mines on the board",
    )
    if not args:
        args = sys.argv[1:]

    opt = parser.parse_args(args)
    minesweeper = Minesweeper()
    curses.wrapper(minesweeper.main, opt.columns, opt.rows, opt.mines)


if __name__ == "__main__":
    main()
