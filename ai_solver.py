'''
ai_solver.py - Rule-based Minesweeper AI (Medium and Hard difficulties)

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

Hard rules: Medium's two rules first, then the 1-2-1 pattern, then the random guess.
    1-2-1 pattern: if three side-by-side revealed numbers read 1-2-1 (after
            subtracting flags already around them) and all their unflagged covered
            neighbors lie in one line beside them, the cells directly across from
            the two 1s are mines and the cell directly across from the 2 is safe.

Inputs:  grid - 2D list of cell.Cell objects (has_mine is never read, so the AI
                cannot cheat; only is_revealed, is_flagged and adjacent_mines are used)
         rng  - optional random source (defaults to the random module) for testing
Outputs: AIMove(action, row, col, rule, source, reason) or None when no covered,
         unflagged cell is left to act on (medium_move, hard_move)

External Sources: Medium and Hard rule definitions from the EECS 581 Project 2 assignment.
                  AI Usage: Claude Code (Claude Opus 5.5) helped restructure the
                  original in-executive solver into this module and write the
                  move-explanation text, and helped write the 1-2-1 pattern search.
                  Combined code is marked below.

Authors: Axel Bengoa, Adam Darst (Medium; original rule loop in executive.py, commit f212149)
         Marcos Lepage, Jal Maru (Hard; effective_number, unknown_neighbors, one_two_one_move, hard_move)
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


def effective_number(grid, row, col):
    # Number minus the flags around it: mines still hidden among its unknown neighbors.
    # Used by the Hard rule; same covered/flagged definitions as deduce_move.
    flagged = [p for p in neighbors(grid, row, col)
               if not grid[p[0]][p[1]].is_revealed and grid[p[0]][p[1]].is_flagged]
    return grid[row][col].adjacent_mines - len(flagged)


def unknown_neighbors(grid, row, col):
    # Covered, unflagged neighbors: the only cells the AI can still act on.
    return [p for p in neighbors(grid, row, col)
            if not grid[p[0]][p[1]].is_revealed and not grid[p[0]][p[1]].is_flagged]


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


def one_two_one_move(grid):
    # Combined: finds three side-by-side numbers reading 1-2-1 (after flags) whose
    # unknown neighbors all lie in one line beside them. In that line, the cells across
    # from the 1s are mines and the cell across from the 2 is safe.
    # One action per call: open the safe cell, then flag a mine.
    size = len(grid)
    # (along, across): direction the three numbers run in, and the direction
    # from the numbers to the line of hidden cells
    orientations = [((0, 1), (-1, 0)), ((0, 1), (1, 0)),   # row of numbers, line above / below
                    ((1, 0), (0, -1)), ((1, 0), (0, 1))]   # column of numbers, line left / right

    def on_board(p):
        return 0 <= p[0] < size and 0 <= p[1] < size

    for row in range(size):
        for col in range(size):
            for (dr, dc), (sr, sc) in orientations:
                left, middle, right = (row - dr, col - dc), (row, col), (row + dr, col + dc)
                trio = [left, middle, right]
                if not all(on_board(p) and grid[p[0]][p[1]].is_revealed for p in trio):
                    continue
                if [effective_number(grid, *p) for p in trio] != [1, 2, 1]:
                    continue

                # The five cells in the line beside the trio (a, b, c, d, e in the doc)
                line = [(row + sr + k * dr, col + sc + k * dc) for k in range(-2, 3)]

                # Any unknown neighbor outside that line means the pattern proves nothing
                unknown = {p for t in trio for p in unknown_neighbors(grid, *t)}
                if not unknown <= set(line):
                    continue

                outer = [line[1], line[3]]  # Across from the 1s: mines
                inner = line[2]             # Across from the 2: safe
                if not all(p in unknown for p in outer):
                    continue  # Board contradicts the pattern (a wrong player flag); don't act on it

                trio_text = "-".join(cell_name(*p) for p in trio)
                raw = [grid[p[0]][p[1]].adjacent_mines for p in trio]
                shown = "" if raw == [1, 2, 1] else f" ({'-'.join(map(str, raw))} minus flags)"

                if inner in unknown:
                    return AIMove("reveal", inner[0], inner[1], "one-two-one", middle,
                                  f"Open {cell_name(*inner)}: 1-2-1 at {trio_text}{shown}")
                target = outer[0]
                return AIMove("flag", target[0], target[1], "one-two-one", middle,
                              f"Flag {cell_name(*target)}: 1-2-1 at {trio_text}{shown}")

    return None


def hard_move(grid, rng=random):
    # Hard difficulty: Medium's counting rules, then the 1-2-1 pattern, otherwise a random guess
    return deduce_move(grid) or one_two_one_move(grid) or guess_move(grid, rng)
