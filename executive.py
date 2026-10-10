'''
Executive Program to run Minesweeper Using Python with PyGame
Inputs: From main.py - runs game when main.py is ran
        From cell.py - uses Cell class to format cells and keep track of cell specfic data
        From user - Before starting, user selects number of mines using slider
                    Ater starting, user selects mine location to either flag with right click or clear with left click

Outputs: Before starting, outputs page with slider for user to select mine count
         After starting, outputs minesweeper gameboard for user interaction
         In case of win, displays win screen
         In case of loss, displays loss screen

External Sources: W3Schools Pygame Tutorial for reference in initializing PyGame: https://www.geeksforgeeks.org/python/pygame-tutorial/
                  RGB color finder:      https://rgb.to/212,210,204
                  AI Usage: ChatGPT with GPT-5.6 Luna Used for creating basic template for PyGame board - further comments in code
                            Claude Used for updating UI to match old school minesweeper style

Authors: Abdulaziz Arab, Felix Balandran, Jamareon Davis, John Vitha, Riley Backus, William Grimsley
Creation Date: September 9, 2026
'''
'''
581 Project 2 Sources:
Authors: Om Ghonasgi
Sources: Tutorial for adding audio to PyGame: https://opensource.com/article/20/9/add-sound-python-game
        Audio files: https://pixabay.com/sound-effects/
        Cursor Agent mode with Claude Opus 4.7
Modified Date: 10/8/2026
'''
'''
581 Project 2 - Medium AI integration:
Authors: Axel Bengoa, Adam Darst
Description: Runs the AI's turns (interactive and automatic) using the strategy in ai_solver.py,
             highlights the cell the AI acted on, and explains each AI move in an info bar under the board.
Sources: Claude Code (Claude Opus 5.5) used to help write the AI turn loop, info bar and highlight drawing.
         Sections written with it are marked "Combined (Claude Code)" below.
Modified Date: 10/10/2026
'''
'''
581 Project 2 - Hard AI integration:
Authors: Marcos Lepage, Jal Maru
Description: Registers ai_solver.hard_move under "Hard" in AI_STRATEGIES so the existing turn loop,
             highlight and info bar run the Hard AI. No other changes to this file.
Sources: Claude Code (Claude Opus 5.5) assisted.
Modified Date: 10/10/2026
'''
from cell import Cell # Import cell class from project folder
import ai_solver # AI strategies (Medium, Hard); kept separate from pygame so the rules can be tested headlessly
import random
import pygame

#Comment types: Critical, Editable, Optional, Explanation

# Editable: This block of code is editable. These are the default values. board starts with each cell being 40x40 pixels, with a board that is 10x10
NUMBER_OF_MINES = 10 # Editable: Default mine count for the grid size (10). This can be changed by the player using the slider, or by future improvisers/maintainers. It's value is later dependent on slider_value
MIN_MINES = 10
MAX_MINES = 20
GRID_SIZE = 10 
CELL_SIZE = 40 


WINDOW_SIZE = GRID_SIZE * CELL_SIZE # Critical/Editable: The values multiplied may be changed, but the logic is critical


#Layout for the retro style: beveled header panel above the board
BORDER = 12 # Editable: Default border size
HEADER_HEIGHT = 56 # Editable: Default Header Height
LABEL_SIZE = 24 # Editable: UI Font size
BOARD_X = BORDER + LABEL_SIZE # Critical: logic for border position
BOARD_Y = BORDER + HEADER_HEIGHT + BORDER + LABEL_SIZE # Critical: logic for border position
WINDOW_WIDTH = BOARD_X + WINDOW_SIZE + BORDER # Critical: adds all widths together to determine window width 
INFO_HEIGHT = 30 # Editable: Height of the info bar under the board that explains AI moves
WINDOW_HEIGHT = BOARD_Y + WINDOW_SIZE + BORDER + INFO_HEIGHT # Critical: adds all heights together to determine window height
SAFE_CELLS = GRID_SIZE * GRID_SIZE - NUMBER_OF_MINES # Critical: calculates non-mine cells. Logic defines game structure. Can't be changed. Excludes mines from the count of cells in the grid
revealed_safe_cells = 0 # Critical: Counter for measuring progress towards end-game. Initializes with player's first click. Guaranteeing a safe start. 

# Button/Slider Initialization
# Details may be changed depending on intent and plans
# Format = feature(x, y, width, height) , (position and size)
button_rect = pygame.Rect(132, 365, 160, 50) # Position the start button below the mode radio buttons
slider_rect = pygame.Rect(112, 236, 200, 12) # Defines the draggable slider handle. 
handle_rect = pygame.Rect(112, 226, 16, 32) # Editable: Create draggable handle for changing mine count
handle_color = (196, 194, 188) # Editable: Sets the slider handle to a light gray color.
slider_color = (150, 148, 142) # Editable Medium grat slider exterior

# Radio button click areas for selecting game mode on the start screen.
# Stacked vertically between the slider handle (bottom ~y=258) and the Start button (y=365)
# so each label has enough horizontal room. Left-aligned at the same x for a clean column.
ai_mode_rect = pygame.Rect(140, 263, 220, 26)        # Click area for the "AI Mode (Interactive)" radio button
ai_auto_mode_rect = pygame.Rect(140, 293, 220, 26)   # Click area for the "AI Mode (Automatic)" radio button
manual_mode_rect = pygame.Rect(140, 323, 220, 26)    # Click area for the "Manual Mode" radio button

# Stores the player's chosen game mode. Set by the radio buttons on the start screen
# and can be referenced later by other game logic (e.g. AI-driven play vs. manual input).
# Valid values: "AI" (interactive AI), "AI_AUTO" (fully automatic AI), or "Manual". Defaults to "Manual".
GAME_MODE = "Manual"

# Difficulty-selection overlay shown AFTER the Start button is clicked, but ONLY when
# GAME_MODE is "AI" or "AI_AUTO". Manual mode skips this screen entirely and goes
# straight to the gameboard.
# The overlay panel is drawn centered on top of the (empty) board so the player sees
# the game in context behind it.
difficulty_overlay_rect = pygame.Rect(70, 130, 328, 340)
easy_rect   = pygame.Rect(140, 240, 220, 26)   # Click area for "Easy"   radio button
medium_rect = pygame.Rect(140, 280, 220, 26)   # Click area for "Medium" radio button
hard_rect   = pygame.Rect(140, 320, 220, 26)   # Click area for "Hard"   radio button
confirm_button_rect = pygame.Rect(144, 400, 160, 50)  # "Confirm" button inside the overlay

# Stores the chosen AI difficulty. Set via the overlay after Start is clicked when
# GAME_MODE is "AI" or "AI_AUTO". Valid values: "Easy", "Medium", "Hard". Defaults to "Easy".
# Can be referenced later by AI logic to tune its behavior.
AI_DIFFICULTY = "Easy"

AI_MOVE_DELAY = 500 # Editable: Milliseconds the AI waits before each action so every move can be watched

# Maps a difficulty name to a function grid -> ai_solver.AIMove (or None when no move is left).
# Add Easy here; a difficulty with no entry leaves the AI idle.
AI_STRATEGIES = {
    "Medium": ai_solver.medium_move,
    "Hard": ai_solver.hard_move,
}


#Retro color palette
FACE = (196, 194, 188) 
REVEALED = (212, 210, 204) 
HIGHLIGHT = (250, 250, 246)
#Editable: Displays varying shades of grey for the aesthetic minesweeper aesthetic

SHADOW = (122, 120, 114)
TEXT_COLOR = (40, 40, 40)

LED_ON = (255, 170, 30)
LED_OFF = (70, 40, 10)
LED_BG = (22, 16, 10)

NUMBER_COLORS = {1: (30, 60, 200), 2: (20, 125, 40), 3: (200, 30, 30), 4: (30, 30, 120),
                 5: (120, 30, 30), 6: (20, 120, 120), 7: (20, 20, 20), 8: (110, 110, 110)}

grid = [[Cell() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
# Critical: Creates board, given each iteration is of cell class, using the range of the grid

# initalize the audio files, and set the volume to 0.5
pygame.mixer.init()
explosion_sound = pygame.mixer.Sound("audio/explosion.mp3")
reveal_sound = pygame.mixer.Sound("audio/reveal.mp3")
flag_sound = pygame.mixer.Sound("audio/flagplace.mp3")
win_sound = pygame.mixer.Sound("audio/win.mp3")

explosion_sound.set_volume(0.5) 
reveal_sound.set_volume(0.5)
flag_sound.set_volume(0.5)
win_sound.set_volume(0.5)

def recursive_sweep(input_row, input_col): # Critical Function: recursively searches for adjacent safe cells using current cell's position
    global revealed_safe_cells

    if grid[input_row][input_col].is_revealed:
        return # Critical: Base Case - if grid is revealed, skip it

    grid[input_row][input_col].is_revealed = True # Base Case - If a cell is revealed and safe (next line)
    revealed_safe_cells += 1 # Base Case - Increment safe cell count. True is used here to represent a cell's safeness
  
    if grid[input_row][input_col].adjacent_mines > 0:
        return # Base Case - if adjacent cells have at least one mine, stop recursion
      
    else: # Otherwise, initiate recursive case
        for row_offset in [-1, 0, 1]: # With respect to adjacent cells (left and right),
            for col_offset in [-1, 0, 1]: # With respect to adjacent cells (up and down)
              
                if row_offset == 0 and col_offset == 0:
                    continue # Skip current tile
                  
                if 0 <= input_row + row_offset < GRID_SIZE and 0 <= input_col + col_offset < GRID_SIZE:
                    recursive_sweep(input_row + row_offset, input_col + col_offset)
                    # Check if adjacent cells are inside of the grid (with respect to vertical & horizontal position) before sweeping
# Function recursive_sweep(row ,column)
# Function used (r,c) as parameter, and different functions moved on to use (input_row,input_col)
# for the sake of consistency and readability, I've changed all row,column variables/parameters to be: (input_row, input_col)


def first_click(input_row, input_col): #Critical Function: logic initializing what happens with the first click
    protected = set() # Member Check: set used to keep account of safe cells of the first click 
    for row_offset in [-1, 0, 1]:
        for col_offset in [-1, 0, 1]:
            if 0 <= input_row + row_offset < GRID_SIZE and 0 <= input_col + col_offset < GRID_SIZE:
                protected.add((input_row+row_offset, input_col+col_offset)) 
    # Safeguard surrounding cells of the first click          

    possible = []
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if (i, j) not in protected:
                possible.append((i, j))
    # If current cell in grid is not protected, then it could be a mine
    # Uses list to preserve order           

    mine_locations = random.sample(possible, NUMBER_OF_MINES)
    for i, j in mine_locations:
        grid[i][j].has_mine = True
    # Place the necessary number of mines randomly on non-protected cells (possibly unsafe)  

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE): # With respect to the Grid(x,y) and adjacent cells
            for row_offset in [-1, 0, 1]:
                for col_offset in [-1, 0, 1]:
                    if row_offset == 0 and col_offset == 0:
                        continue # Skip current cells
                    if 0 <= i + row_offset < GRID_SIZE and 0 <= j + col_offset < GRID_SIZE: # Explanation: Checks cells inside the grid first to avoid indexing errors
                        if grid[i+row_offset][j+col_offset].has_mine: # Then checks if there is a mine
                            grid[i][j].adjacent_mines += 1 # If so, increment adjacent mine count
                    # Can be reduced to one if statement, but this can also help with readability and understanding the process      

    recursive_sweep(input_row, input_col)
    reveal_sound.play()
  # Start flood filled, recursive reveal from the first clicked cell


def reveal(input_row, input_col): # Critical Function: Uses the recursive sweeps to reveal mines.
    if grid[input_row][input_col].has_mine:
        return False # Base Case - if the cell has a mine
    reveal_sound.play()
    recursive_sweep(input_row, input_col) # Uses the recursive sweeps to reveal mines.

    if revealed_safe_cells == SAFE_CELLS:
        return "win"
    # If all of the safe cells have been revealed, end the game announcing the player's win  

    return True

_fonts = {}
# Used for get_font
def get_font(size, bold=False): # Editable function: returns cache font for 
    #Cache fonts so they aren't recreated for every cell every frame
    if (size, bold) not in _fonts:
        font = pygame.font.Font(None, size)
        font.set_bold(bold)
        _fonts[(size, bold)] = font
    return _fonts[(size, bold)]


def draw_bevel(screen, rect, raised=True, width=3): # Editable: Draws Bevel(self explanatory)
    #Light edge top/left and dark edge bottom/right gives the raised 3D look
    light, dark = (HIGHLIGHT, SHADOW) if raised else (SHADOW, HIGHLIGHT)
    for i in range(width):
        left, top = rect.left + i, rect.top + i
        right, bottom = rect.right - 1 - i, rect.bottom - 1 - i
        pygame.draw.line(screen, dark, (left, bottom), (right, bottom))
        pygame.draw.line(screen, dark, (right, top), (right, bottom))
        pygame.draw.line(screen, light, (left, top), (right, top))
        pygame.draw.line(screen, light, (left, top), (left, bottom))


def draw_mine(screen, cx, cy):
    r = CELL_SIZE // 5
    spike = r + 6
    for dx, dy in [(1, 0), (0, 1), (0.7, 0.7), (0.7, -0.7)]:
        pygame.draw.line(screen, (20, 20, 20), (cx - dx * spike, cy - dy * spike),
                         (cx + dx * spike, cy + dy * spike), 3)
    pygame.draw.circle(screen, (20, 20, 20), (cx, cy), r)
    pygame.draw.circle(screen, (235, 235, 235), (cx - r // 3, cy - r // 3), max(2, r // 3))


def draw_flag(screen, cx, cy):
    pygame.draw.rect(screen, (20, 20, 20), (cx - 9, cy + 9, 18, 3))
    pygame.draw.rect(screen, (20, 20, 20), (cx - 5, cy + 6, 10, 3))
    pygame.draw.line(screen, (20, 20, 20), (cx + 1, cy - 11), (cx + 1, cy + 7), 2)
    pygame.draw.polygon(screen, (205, 25, 25), [(cx + 2, cy - 12), (cx + 2, cy - 1), (cx - 10, cy - 6)])


SEGMENTS = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd",
            "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg", "-": "g"}
# Display each number of a cell with a certain aesthetic



def draw_counter(screen, value, x, y):
    #Three digit seven-segment readout in a sunken box
    text = "-" + f"{min(-value, 99):02d}" if value < 0 else f"{min(value, 999):03d}"
    box = pygame.Rect(x, y, 70, 38)
    pygame.draw.rect(screen, LED_BG, box)
    draw_bevel(screen, box, raised=False, width=2)
    w, h, t = 15, 28, 3
    for i, ch in enumerate(text):
        sx, sy = x + 7 + i * 20, y + 5
        segs = {
            "a": (sx + t, sy, w - 2 * t, t),
            "b": (sx + w - t, sy + t, t, h // 2 - t),
            "c": (sx + w - t, sy + h // 2, t, h // 2 - t),
            "d": (sx + t, sy + h - t, w - 2 * t, t),
            "e": (sx, sy + h // 2, t, h // 2 - t),
            "f": (sx, sy + t, t, h // 2 - t),
            "g": (sx + t, sy + h // 2 - 1, w - 2 * t, t),
        }
        for name, r in segs.items():
            pygame.draw.rect(screen, LED_ON if name in SEGMENTS[ch] else LED_OFF, r)


def draw_plate(screen, rect, label, color):
    pygame.draw.rect(screen, FACE, rect)
    draw_bevel(screen, rect, raised=True, width=3)
    text = get_font(26, bold=True).render(label, True, color)
    screen.blit(text, text.get_rect(center=rect.center))


def draw_radio(screen, rect, label, selected):
    # Draws a classic circular radio button at the left edge of rect, with the
    # label text to its right. When selected is True, fills in the inner dot.
    cx = rect.left + 10
    cy = rect.centery
    pygame.draw.circle(screen, REVEALED, (cx, cy), 9)       # Light inset background
    pygame.draw.circle(screen, SHADOW, (cx, cy), 9, 2)      # Dark ring outline
    if selected:
        pygame.draw.circle(screen, TEXT_COLOR, (cx, cy), 4) # Filled dot = chosen
    text = get_font(22, bold=True).render(label, True, TEXT_COLOR)
    screen.blit(text, text.get_rect(midleft=(cx + 14, cy)))


def draw_difficulty_overlay(screen):
    # Beveled panel centered on top of the board, matching the retro UI style.
    # Shown only when GAME_MODE is "AI" or "AI_AUTO" after the Start button is clicked.
    pygame.draw.rect(screen, FACE, difficulty_overlay_rect)
    draw_bevel(screen, difficulty_overlay_rect, raised=True, width=3)

    # Title
    title = get_font(32, bold=True).render("Select AI Difficulty", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(difficulty_overlay_rect.centerx,
                                              difficulty_overlay_rect.top + 40)))
    # Mutually exclusive radio buttons
    draw_radio(screen, easy_rect,   "Easy",   AI_DIFFICULTY == "Easy")
    draw_radio(screen, medium_rect, "Medium", AI_DIFFICULTY == "Medium")
    draw_radio(screen, hard_rect,   "Hard",   AI_DIFFICULTY == "Hard")

    # Confirm button to lock in the choice and proceed to the game
    draw_plate(screen, confirm_button_rect, "Confirm", TEXT_COLOR)


def draw_cell(screen, row, col, outcome=None, exploded=None):
    x = BOARD_X + col * CELL_SIZE
    y = BOARD_Y + row * CELL_SIZE
    rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
    cx, cy = rect.center
    #This block of code was adapted from ChatGPT 5.6-Luina when asking how to setup a gameboard in pygame
    #All code was subesequently written manually, but it was adapted from the AI
    #The cell visuals were later restyled (bevels, drawn mines and flags) with help from Claude
    #After a loss, mines are drawn face up here without changing any cell state
    show_mine = outcome == "lost" and grid[row][col].has_mine and not grid[row][col].is_flagged
    if grid[row][col].is_revealed or show_mine:
        bg = (220, 40, 40) if (row, col) == exploded else REVEALED
        pygame.draw.rect(screen, bg, rect)
        pygame.draw.rect(screen, SHADOW, rect, 1)
        if grid[row][col].has_mine:
            draw_mine(screen, cx, cy)
        elif grid[row][col].adjacent_mines > 0:
            n = grid[row][col].adjacent_mines
            text = get_font(34, bold=True).render(str(n), True, NUMBER_COLORS[n])
            screen.blit(text, text.get_rect(center=(cx, cy + 1)))
    else:
        pygame.draw.rect(screen, FACE, rect)
        draw_bevel(screen, rect, raised=True, width=3)
        if grid[row][col].is_flagged:
            if outcome == "lost" and not grid[row][col].has_mine:
                #Wrong flag: crossed-out mine
                draw_mine(screen, cx, cy)
                pygame.draw.line(screen, (200, 20, 20), (x + 8, y + 8), (x + CELL_SIZE - 9, y + CELL_SIZE - 9), 3)
                pygame.draw.line(screen, (200, 20, 20), (x + CELL_SIZE - 9, y + 8), (x + 8, y + CELL_SIZE - 9), 3)
            else:
                draw_flag(screen, cx, cy)


def draw_board(screen, outcome=None, exploded=None):
    board = pygame.Rect(BOARD_X - 3, BOARD_Y - 3, WINDOW_SIZE + 6, WINDOW_SIZE + 6)
    draw_bevel(screen, board, raised=False, width=3)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            draw_cell(screen, row, col, outcome, exploded)

def draw_labels(screen):
    #Column letters (A-J) above the board, row numbers (1-10) to the left
    font = get_font(20, bold=True)
    for col in range(GRID_SIZE):
        letter = chr(ord('A') + col)
        text = font.render(letter, True, TEXT_COLOR)
        x = BOARD_X + col * CELL_SIZE + CELL_SIZE // 2
        y = BOARD_Y - LABEL_SIZE // 2 - 2
        screen.blit(text, text.get_rect(center=(x, y)))

    for row in range(GRID_SIZE):
        number = str(row + 1)
        text = font.render(number, True, TEXT_COLOR)
        x = BOARD_X - LABEL_SIZE // 2 - 2
        y = BOARD_Y + row * CELL_SIZE + CELL_SIZE // 2
        screen.blit(text, text.get_rect(center=(x, y)))


def draw_header(screen, outcome, seconds, status=None):
    #Mines left on the left, status plate in the middle, timer on the right
    #status is an optional (label, color) pair that replaces the plate text in the AI modes
    panel = pygame.Rect(BORDER - 3, BORDER - 3, WINDOW_WIDTH - 2 * BORDER + 6, HEADER_HEIGHT + 6)
    draw_bevel(screen, panel, raised=False, width=3)
    flags = sum(cell.is_flagged for grid_row in grid for cell in grid_row)
    draw_counter(screen, NUMBER_OF_MINES - flags, BORDER + 8, BORDER + 9)
    draw_counter(screen, seconds, WINDOW_WIDTH - BORDER - 78, BORDER + 9)
    plate = pygame.Rect((WINDOW_WIDTH - 150) // 2, BORDER + 11, 150, 34)
    if status is not None:
        draw_plate(screen, plate, status[0], status[1])
    elif outcome == "won":
        draw_plate(screen, plate, "You Win!", (20, 125, 40))
    elif outcome == "lost":
        draw_plate(screen, plate, "Boom!", (180, 30, 30))
    else:
        draw_plate(screen, plate, "Minesweeper", TEXT_COLOR)


# Combined (Claude Code): info bar and highlight drawing for the AI modes
def draw_info_bar(screen, text):
    #Sunken strip under the board; explains the AI's last move (or shows the controls in Manual mode)
    bar = pygame.Rect(BORDER - 3, BOARD_Y + WINDOW_SIZE + BORDER - 3, WINDOW_WIDTH - 2 * BORDER + 6, INFO_HEIGHT - 2)
    pygame.draw.rect(screen, REVEALED, bar)
    draw_bevel(screen, bar, raised=False, width=2)
    for size in (22, 19, 16): #Shrink long explanations until they fit the bar
        label = get_font(size, bold=True).render(text, True, TEXT_COLOR)
        if label.get_width() <= bar.width - 12:
            break
    screen.blit(label, label.get_rect(center=bar.center))


def draw_ai_highlight(screen, move):
    #Outline the cell the AI acted on (orange) and the number that justified it (blue)
    if move is None:
        return
    if move.source is not None:
        x = BOARD_X + move.source[1] * CELL_SIZE
        y = BOARD_Y + move.source[0] * CELL_SIZE
        pygame.draw.rect(screen, (30, 60, 200), (x, y, CELL_SIZE, CELL_SIZE), 3)
    x = BOARD_X + move.col * CELL_SIZE
    y = BOARD_Y + move.row * CELL_SIZE
    pygame.draw.rect(screen, (230, 120, 0), (x, y, CELL_SIZE, CELL_SIZE), 3)


def run_game():
        
    global NUMBER_OF_MINES # Critical: Variable is effected throughout multiple functions and thus should stay global
    global SAFE_CELLS
    global GAME_MODE # Tracks the player's selected game mode ("AI", "AI_AUTO", or "Manual") from the start screen radio buttons
    global AI_DIFFICULTY # Tracks the chosen AI difficulty ("Easy", "Medium", "Hard") selected on the overlay after Start
    # Variable is effected throughout multiple functions and thus should stay global

     # This block initializes the starting conditions of the game; as a window of a certain size displaying what it's for, and starting off with most conditions being at zero or the bare minimum   
    pygame.init()

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) # Initializes the size of the window to be the size of the board
    pygame.display.set_caption("Minesweeper") # Set window name to be "Minesweeper"
    first_move_done = False # Game starts off letting the user do the first move
    game_over = False # Game starts off as active/playable until player loses
        
    dragging=False # Starts off with the slider being motionless
    slider_value_picked = False 
    slider_value = 10

    # Tracks whether the AI difficulty overlay has been dismissed.
    # Manual mode never shows the overlay so it's effectively True from the start of the game screen;
    # for AI / AI_AUTO modes it stays False until the player confirms a difficulty.
    difficulty_picked = False

    # AI state: whether an AI strategy is playing, whose turn it is, when the AI may act next,
    # the AI's last move (for the highlight/info bar) and the end-of-game plate text
    ai_active = False
    ai_turn = False
    ai_move_at = 0
    ai_last_move = None
    ai_message = ""
    end_status = None

    #Display-only state for the header and loss screen
    outcome = None
    exploded = None
    start_ticks = 0
    seconds = 0

    #Game loop set up with reference from Geeks to Geeks PyGame tutorial
    while True:
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
         # As long as the player doesn't quit, return every other action/event type           



         # Checks for slider value picking by waiting for user input through the mouse
            if not slider_value_picked:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if handle_rect.collidepoint(event.pos):
                        dragging = True
                    elif button_rect.collidepoint(event.pos):
                        slider_value_picked = True
                        # Manual mode skips the difficulty overlay; AI modes must still pick one.
                        difficulty_picked = (GAME_MODE == "Manual")
                    # Mutually exclusive mode selection: clicking a radio button overrides the others
                    elif ai_mode_rect.collidepoint(event.pos):
                        GAME_MODE = "AI"
                    elif ai_auto_mode_rect.collidepoint(event.pos):
                        GAME_MODE = "AI_AUTO"
                    elif manual_mode_rect.collidepoint(event.pos):
                        GAME_MODE = "Manual"
                elif event.type == pygame.MOUSEBUTTONUP:
                    dragging = False
                elif event.type == pygame.MOUSEMOTION and dragging:
                    mouse_x, _ = event.pos
                    #This line was generated by ChatGPT GPT-5.6 Luna when asking how to get the slider handle to stay on the track and centered
                    #It was then edited to use mouse_x as it was initially event.pos[0] but mouse_x is used multiple times
                    handle_rect.x = max(slider_rect.x, min(mouse_x - handle_rect.width//2, slider_rect.right - handle_rect.width))

                     # slider works on a scale of a precentage, and here its being defined in terms of functionality   
                    slider_percent = (mouse_x - slider_rect.x) / slider_rect.width
                    slider_percent = max(0, min(1, slider_percent))
                    slider_value = round(MIN_MINES + slider_percent * (MAX_MINES - MIN_MINES))

                    # Determine/set slider value and associate it with the number of mines, then calculate the number of safe cells
                if slider_value_picked:
                    NUMBER_OF_MINES = slider_value
                    SAFE_CELLS=GRID_SIZE * GRID_SIZE - NUMBER_OF_MINES

                    

            # Difficulty-selection overlay: shown only in AI / AI_AUTO modes.
            # Blocks board input until the player confirms a difficulty.
            elif not difficulty_picked:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Mutually exclusive difficulty selection
                    if easy_rect.collidepoint(event.pos):
                        AI_DIFFICULTY = "Easy"
                    elif medium_rect.collidepoint(event.pos):
                        AI_DIFFICULTY = "Medium"
                    elif hard_rect.collidepoint(event.pos):
                        AI_DIFFICULTY = "Hard"
                    elif confirm_button_rect.collidepoint(event.pos):
                        difficulty_picked = True
                        ai_active = AI_DIFFICULTY in AI_STRATEGIES
                        if ai_active and GAME_MODE == "AI_AUTO":
                            ai_turn = True # Automatic mode: the AI also makes the first move
                            ai_move_at = pygame.time.get_ticks() + AI_MOVE_DELAY
                            ai_message = f"{AI_DIFFICULTY} AI is playing"
                        elif ai_active:
                            ai_message = f"Your move first, then {AI_DIFFICULTY} AI replies"

            # If player clicks anywhere in the game and it doesn't end (can be revealing tile or clicking on the window or a revealed tile),
            # Clicks are ignored while the AI is taking its turn (always the case in automatic mode)
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over and not ai_turn:
                col = (event.pos[0] - BOARD_X)//CELL_SIZE
                row = (event.pos[1] - BOARD_Y)//CELL_SIZE


                    # Bound check: making sure the mouse click is on a valid cell, the first move, if the tile is flagged before the logic occurs
                if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE: 
                    if event.button == 1:
                        if not grid[row][col].is_flagged:
                            was_hidden = not grid[row][col].is_revealed
                            if not first_move_done:
                                first_click(row, col)
                                first_move_done = True
                                start_ticks = pygame.time.get_ticks()
                            else:
                                result = reveal(row, col)
                                if not result:
                                    game_over = True
                                    print("Boom.")
                                    outcome = "lost"
                                    # Play the sound effect when an explosion happens
                                    explosion_sound.play()
                                    exploded = (row, col)
                                elif result == "win":
                                    game_over = True
                                    print("You win!")
                                    win_sound.play()
                                    outcome = "won"

                            # Interactive AI mode: opening a covered cell ends the player's turn
                            # (flagging does not, flags are the player's own notes)
                            if ai_active and GAME_MODE == "AI":
                                if outcome == "lost":
                                    end_status = ("AI Wins!", (180, 30, 30))
                                elif outcome == "won":
                                    end_status = ("Both Win!", (20, 125, 40))
                                elif was_hidden:
                                    ai_turn = True
                                    ai_move_at = pygame.time.get_ticks() + AI_MOVE_DELAY
                    elif event.button == 3:
                        if not grid[row][col].is_revealed:
                            if grid[row][col].is_flagged:
                                grid[row][col].is_flagged = False
                            else:
                                grid[row][col].is_flagged = True
                                flag_sound.play()

        # Combined (Claude Code): AI turn. Asks the selected strategy for ONE action and applies it,
        # so each flag/open is visible for AI_MOVE_DELAY ms before the next one
        if ai_turn and not game_over and pygame.time.get_ticks() >= ai_move_at:
            move = AI_STRATEGIES[AI_DIFFICULTY](grid)
            if move is None:
                # Only covered cells left are flagged (possible when the player flagged a safe cell)
                ai_turn = False
                ai_message = "AI has no move left, your turn"
            else:
                ai_last_move = move
                ai_message = move.reason
                print("AI:", move.reason)
                result = True
                if move.action == "flag":
                    grid[move.row][move.col].is_flagged = True
                    flag_sound.play()
                elif not first_move_done:
                    # The AI opens the game in automatic mode: same safe first click as a human
                    first_click(move.row, move.col)
                    first_move_done = True
                    start_ticks = pygame.time.get_ticks()
                    ai_last_move = ai_solver.AIMove("reveal", move.row, move.col, "guess", None,
                                                    f"Open {ai_solver.cell_name(move.row, move.col)}: first move")
                    ai_message = ai_last_move.reason
                    if revealed_safe_cells == SAFE_CELLS:
                        result = "win"
                else:
                    result = reveal(move.row, move.col)

                if not result:
                    game_over = True
                    print("Boom.")
                    outcome = "lost"
                    explosion_sound.play()
                    exploded = (move.row, move.col)
                    end_status = ("You Win!", (20, 125, 40)) if GAME_MODE == "AI" else ("AI Lost", (180, 30, 30))
                elif result == "win":
                    game_over = True
                    win_sound.play()
                    outcome = "won"
                    end_status = ("Both Win!", (20, 125, 40)) if GAME_MODE == "AI" else ("AI Wins!", (20, 125, 40))

                ai_turn = GAME_MODE == "AI_AUTO" # Interactive mode hands the turn back after one action
                ai_move_at = pygame.time.get_ticks() + AI_MOVE_DELAY

        if not slider_value_picked:
            #draw the slider
            screen.fill(FACE)
            draw_bevel(screen, pygame.Rect(BORDER, BORDER, WINDOW_WIDTH - 2 * BORDER, WINDOW_HEIGHT - 2 * BORDER), raised=False)
            title = get_font(64).render("MINESWEEPER", True, TEXT_COLOR)
            screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 80)))
            draw_mine(screen, WINDOW_WIDTH // 2, 132)
            label = get_font(28, bold=True).render("Mines:", True, TEXT_COLOR)
            screen.blit(label, label.get_rect(midright=(WINDOW_WIDTH // 2 - 6, 190)))
            draw_counter(screen, slider_value, WINDOW_WIDTH // 2 + 4, 171)
            pygame.draw.rect(screen, slider_color, slider_rect)
            draw_bevel(screen, slider_rect, raised=False, width=2)
            pygame.draw.rect(screen, handle_color, handle_rect)
            draw_bevel(screen, handle_rect)

            # draw the mode-selection radio buttons (mutually exclusive)
            draw_radio(screen, ai_mode_rect, "AI Mode (Interactive)", GAME_MODE == "AI")
            draw_radio(screen, ai_auto_mode_rect, "AI Mode (Automatic)", GAME_MODE == "AI_AUTO")
            draw_radio(screen, manual_mode_rect, "Manual Mode", GAME_MODE == "Manual")

            #draw the start button
            draw_plate(screen, button_rect, "Start", TEXT_COLOR)
            hint = get_font(22).render("Left click: reveal    Right click: flag", True, (80, 80, 80))
            screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40)))
        else:
            if first_move_done and not game_over:
                seconds = min(999, (pygame.time.get_ticks() - start_ticks) // 1000)
            screen.fill(FACE)
            # Header plate in the AI modes: the result once the game ends, otherwise whose turn it is
            status = end_status
            if status is None and ai_active and not game_over:
                if ai_turn:
                    status = ("AI's Turn", (200, 100, 0))
                else:
                    status = ("Your Turn", (30, 60, 200))
            draw_header(screen, outcome, seconds, status)
            draw_labels(screen)
            draw_board(screen, outcome, exploded)
            if ai_active:
                draw_ai_highlight(screen, ai_last_move)
                draw_info_bar(screen, ai_message)
            else:
                draw_info_bar(screen, "Left click: reveal    Right click: flag")

            # Draw the AI difficulty overlay on top of the (empty) board so the
            # player sees the game context behind the modal. Only reached when
            # GAME_MODE is "AI" or "AI_AUTO" because Manual mode sets
            # difficulty_picked = True immediately after Start.
            if not difficulty_picked:
                draw_difficulty_overlay(screen)
        pygame.display.flip()
