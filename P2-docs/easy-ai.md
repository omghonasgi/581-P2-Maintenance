# Easy AI Solver — Architecture

Author: Arin Shah · Last updated: 2026-10-11

## What it does

The Easy AI plays on the same 10×10 board as the human and uses no strategy. Each turn it opens **one** cell, chosen completely at random from the cells that are still covered and not flagged. It never flags, never looks at the numbers on the board and never reads `Cell.has_mine`, so it cannot cheat and cannot do better than chance.

## How it works

The whole AI is one function, `easy_ai_move(board)` in `executive.py`:

1. Collect every cell that is not revealed and not flagged into a list.
2. If the list is empty, return `None` (the AI has nothing to pick).
3. Otherwise choose an index with `random.randint(0, len(remaining) - 1)` and return that cell as a `"reveal"` move.

Every remaining cell is equally likely, whether it hides a mine or not. Flagged cells are skipped because the specification says the Easy AI avoids flagged and uncovered cells; in interactive mode this lets the player protect a cell by flagging it.

The function returns the same `AIMove` record that Medium and Hard use, and is registered with `AI_STRATEGIES["Easy"] = easy_ai_move`. Because of that, the shared turn loop in `run_game` runs it with no Easy-specific code: the loop applies the move, plays the sounds, checks for a win or loss, outlines the picked cell and shows a line such as `Open C4: random pick` in the info bar.

## Turn flow

- **AI Mode (Automatic):** the AI plays alone. Its first pick goes through `first_click`, so it is safe and deals the board, same as a human's first click. It then opens one random cell every `AI_MOVE_DELAY` ms until it hits a mine (`AI Lost`) or clears the board (`AI Wins!`). Mouse clicks on the board are ignored.
- **AI Mode (Interactive):** the player moves first. Opening a covered cell passes the turn to the AI; placing a flag does not. The AI opens one random cell and hands the turn back. The header plate shows `Your Turn` / `AI's Turn`, then the result: `AI Wins!` (the player hit a mine), `You Win!` (the AI hit a mine) or `Both Win!` (board cleared).

## Measured behavior

2,000 simulated automatic games per row, run headlessly against the real `first_click`/`reveal` code.

| Mines | Easy win rate | Average picks per game |
|---|---|---|
| 10 | 0.0% | 4.1 |
| 15 | 0.0% | 4.7 |
| 20 | 0.0% | 4.6 |

Picks include the safe first move and the final pick that hits a mine. In interactive mode this means a careful player usually wins within a few turns.

## AI attribution

Arin Shah specified the Easy behavior from the project requirements. He wrote the code in conjunction with Claude Model Opus 5.5 in which it helped to write documentation and merge it into the maintenence branch with minor edits
