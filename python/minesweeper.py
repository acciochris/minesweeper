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
        self.cells = []
        for _ in range(self.cols):
            self.cells.append([Cell() for _ in range(self.rows)])

    def _neighbors(self, pos: tuple[int, int]) -> dict[tuple[int, int], Cell]:
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

    def _flag_count(self, pos: tuple[int, int]) -> int:
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
        poses = [(x, y) for x in range(self.cols) for y in range(self.rows)]
        mines = random.sample([pos for pos in poses if pos != start], self.mines)

        for x, y in mines:
            self.cells[x][y].mine = True

        # Calculate Cell.mine_count
        for x, y in poses:
            cell = self.cells[x][y]
            for neighbor in self._neighbors((x, y)).values():
                if neighbor.mine:
                    cell.mine_count += 1

    def uncover(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
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

    def __init__(self, cols=9, rows=9, mines=10):
        self.board = Board(cols, rows, mines)

    def main(self, stdscr: curses._CursesWindow):
        """The main entry point for the game"""
        # Initialize everything
        stdscr.clear()
        stdscr.refresh()

        curses.curs_set(0)
        stdscr_y, stdscr_x = stdscr.getmaxyx()
        if (self.board.rows > stdscr_y) or (self.board.cols > stdscr_x):
            raise RuntimeError("Screen is too small!")
        board_win = curses.newwin(self.board.rows + 1, self.board.cols + 1)
        self.init_board(board_win)

        # Main loop
        while True:
            c = stdscr.getch()
            if 0 < c < 256:
                c = chr(c)
                if c in "Qq":
                    break

    def init_board(self, win: curses._CursesWindow):
        """Initialize the board in `win`"""
        for y in range(self.board.rows):
            for x in range(self.board.cols):
                win.addstr(y, x, "-")
        win.refresh()


def main(args=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-c",
        "--cols",
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

    config = parser.parse_args(args)
    minesweeper = Minesweeper(config.cols, config.rows, config.mines)
    curses.wrapper(minesweeper.main)


if __name__ == "__main__":
    main()
