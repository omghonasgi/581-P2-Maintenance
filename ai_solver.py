'''
ai_solver.py - Rule-based Minesweeper AI (Medium difficulty)

Description: Decides the AI's next move from the current board. The solver never
             changes the board itself; it returns an AIMove describing what to do
             and why, and executive.py applies it (flag, reveal, sounds, win/loss).
             This keeps the rules independent of pygame so they can be tested
             headlessly and so other difficulties can be added beside them.

Medium rules (from the EECS 581 Project 2 specification):
    Rule 1 (flag by count): if a revealed number equals the number of COVERED
            neighbors it has (flagged or not), every covered neighbor is a mine,
            so flag one that is not flagged yet.
    Rule 2 (open by count): if a revealed number equals the number of FLAGGED
            neighbors it has, every other covered neighbor is safe, so open one.
    Fallback: if neither rule applies anywhere, open a random covered, unflagged cell.
    The AI makes exactly one action per call so every move is visible on screen.

Inputs:  grid - 2D list of cell.Cell objects (has_mine is never read, so the AI
                cannot cheat; only is_revealed, is_flagged and adjacent_mines are used)
         rng  - optional random source (defaults to the random module) for testing
Outputs: AIMove(action, row, col, rule, source, reason) or None when no covered,
         unflagged cell is left to act on

External Sources: Medium rule definitions from the EECS 581 Project 2 assignment.
                  AI Usage: Claude Code (Claude Opus 5.5) helped restructure the
                  original in-executive solver into this module and write the
                  move-explanation text. Combined code is marked below.

Authors: Axel Bengoa, Adam Darst (original rule loop in executive.py, commit f212149)
Creation Date: October 10, 2026
'''
import random


class AIMove:
    # Plain record describing one AI action. Original code.
    def __init__(self, action, row, col, rule, source=None, reason=""):
        self.action = action    # "flag" or "reveal"
        self.row = row
        self.col = col
        self.rule = rule        # "flag-count", "open-count" or "guess"
        self.source = source    # (row, col) of the number that justified the move, or None for a guess
        self.reason = reason    # Short human-readable explanation shown on screen


def cell_name(row, col):
    # Matches the board labels drawn by executive.draw_labels: columns A-J, rows 1-10
    return chr(ord('A') + col) + str(row + 1)


def neighbors(grid, input_row, input_col):
    # Valid positions surrounding a cell (same offsets as executive.recursive_sweep)
    size = len(grid)
    cells = []
    for row_offset in [-1, 0, 1]:
        for col_offset in [-1, 0, 1]:
            if row_offset == 0 and col_offset == 0:
                continue
            row = input_row + row_offset
            col = input_col + col_offset
            if 0 <= row < size and 0 <= col < size:
                cells.append((row, col))
    return cells


def deduce_move(grid):
    # Combined: rule loop adapted from Adam Darst's ai_solver_step, restructured
    # with Claude Code to return a move + explanation instead of acting directly.
    # Returns the first rule 1 / rule 2 move found, or None if no rule applies.
    for row in range(len(grid)):
        for col in range(len(grid)):
            current = grid[row][col]
            if not current.is_revealed or current.adjacent_mines == 0:
                continue  # Only revealed numbers give information

            number = current.adjacent_mines
            # "Covered" counts flagged cells too: a flag still hides the cell.
            # A cell can be both revealed and flagged if flood fill swept over a flag,
            # so is_revealed is checked first to keep those out of every list.
            covered = [p for p in neighbors(grid, row, col) if not grid[p[0]][p[1]].is_revealed]
            flagged = [p for p in covered if grid[p[0]][p[1]].is_flagged]
            unknown = [p for p in covered if not grid[p[0]][p[1]].is_flagged]

            if not unknown:
                continue  # Nothing left to act on around this number; avoids no-op moves

            here = cell_name(row, col)

            # Rule 1: every covered neighbor must be a mine
            if len(covered) == number:
                target = unknown[0]
                return AIMove("flag", target[0], target[1], "flag-count", (row, col),
                              f"Flag {cell_name(*target)}: {here} is a {number} "
                              f"with {number} covered")

            # Rule 2: all mines around this number are already flagged
            if len(flagged) == number:
                target = unknown[0]
                return AIMove("reveal", target[0], target[1], "open-count", (row, col),
                              f"Open {cell_name(*target)}: {here} is a {number} "
                              f"with {number} flagged")

    return None


def guess_move(grid, rng=random):
    # Fallback: open a random covered, unflagged cell (None if there is none)
    choices = [(row, col) for row in range(len(grid)) for col in range(len(grid))
               if not grid[row][col].is_revealed and not grid[row][col].is_flagged]
    if not choices:
        return None
    row, col = rng.choice(choices)
    return AIMove("reveal", row, col, "guess", None,
                  f"Guess {cell_name(row, col)}: no rule applies")


def medium_move(grid, rng=random):
    # Medium difficulty: the two counting rules, otherwise a random guess
    return deduce_move(grid) or guess_move(grid, rng)
