# Minesweeper (EECS 581 – Project 1, Group 5)

Minesweeper built in Python with [Pygame](https://www.pygame.org/). Reveal every safe cell on the board without detonating a mine, flag the ones you suspect, and use number clues to work out where the mines are hiding.


## Features

- **Configurable mine count**, before the board is dealt, drag the on-screen slider to choose anywhere from 10 to 20 mines, then press **Start**.
- **10x10 grid board** rendered with Pygame, with each cell drawn as an individual clickable tile.
- **Safe first click** — the first cell you reveal (and its immediate neighbors) is guaranteed to never contain a mine; mines are only placed after your first move.
- **Flood-fill reveal**, clicking a cell with zero adjacent mines automatically reveals all of its connected empty neighbors, just like the original Minesweeper.
- **Adjacent mine counts**, revealed cells that border at least one mine display the number of mines touching them.
- **Flagging**, right-click any hidden cell to mark it as a suspected mine (and right-click again to unflag it).
- **Rule-based AI (Medium)**, select **AI Mode (Interactive)** to alternate turns with the AI (you move first), or **AI Mode (Automatic)** to watch it play the whole board, then pick **Medium** on the difficulty screen. The AI makes one action per turn: it flags covered neighbors when a number equals its covered-neighbor count, opens covered neighbors when a number already has that many flags, and otherwise guesses a random covered cell. The bar under the board explains each move, and the cell it acted on (orange) and the number that justified it (blue) are outlined. See [`documentation/medium-ai.md`](documentation/medium-ai.md).
- **Rule-based AI (Hard)**, pick **Hard** on the difficulty screen. The AI uses the Medium rules and adds the 1-2-1 pattern: when three side-by-side numbers read 1-2-1 along a line of covered cells, it opens the cell across from the 2 and flags the cells across from the 1s. If no rule applies, it guesses. See [`documentation/hard-ai.md`](documentation/hard-ai.md).
- **Win/Loss detection**, the game ends the moment you reveal a mine (loss) or reveal every non-mine cell on the board (win).

## Installation

These steps assume you have [Python 3](https://www.python.org/downloads/) installed and available on your `PATH`.

1. **Clone the repository**

   ```bash
   git clone https://github.com/flec1115/581_p1_g5.git
   cd 581_p1_g5
   ```

2. **Create and activate a virtual environment** (recommended)

   ```bash
   python3 -m venv env
   source env/bin/activate      # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install pygame
   ```

## Running the Game

With your virtual environment activated, run:

```bash
python3 main.py
```

A window titled **"Minesweeper"** will open.

## How to Play / Controls

1. **Set the mine count**, drag the slider handle left/right to choose a mine count between 10 and 20, then click the green **Start** button.
2. **Left-click** a hidden cell to reveal it.
   - If it's a mine, the game ends immediately.
   - If it's empty (no adjacent mines), all connected empty cells are revealed automatically.
   - If it has adjacent mines, the number of neighboring mines is displayed.
3. **Right-click** a hidden cell to place or remove a flag (`F`) on a cell you believe contains a mine.
4. **Win condition**, reveal every cell that does not contain a mine.
5. **Lose condition**, reveal a cell that contains a mine.
6. Close the window (or press the window's close button) to quit at any time.

## Project Documentation

Additional project documentation for the team lives in the [`docs/`](docs) directory:

- [`docs/architecture.md`](docs/architecture.md) — technical design and architecture notes
- [`docs/hours-estimate.md`](docs/hours-estimate.md) — estimated hours per task/team member
- [`docs/hours-actual.md`](docs/hours-actual.md) — actual hours spent per task/team member
- [`docs/meeting-log.md`](docs/meeting-log.md) — team meeting notes/log

## Team Members

| Name | Role | GitHub |
| ---- | ---- | ------ |
|Abdulaziz Arab|Technical Writer|@REVERSED-HERMIT|
|Riley Backus|Software Tester|@rileybackus96|
|Felix Balandran|Technical Writer|@flec1115|
|Jamareon Davis|UI Developer|@jamareond|
|William Grimsley|Frontend Developer|@wkgrimsley|
|John Vitha|Backend Developer|@johnvitha2|
