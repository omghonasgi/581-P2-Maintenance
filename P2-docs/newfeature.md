# New Features — Mode Selection, AI Difficulty, and Sound

Author: Om Ghonasgi · Last updated: 2026-10-11

Three UI and audio additions in `executive.py`. They sit in front of the AI solvers and do not change the board rules.

## Game mode

On the start screen, below the mine slider, the player picks one radio:

| Radio | `GAME_MODE` | Behavior |
| ----- | ----------- | -------- |
| AI Mode (Interactive) | `"AI"` | Player moves first; the AI replies after each reveal |
| AI Mode (Automatic) | `"AI_AUTO"` | The AI plays the whole board |
| Manual Mode | `"Manual"` | Original human-only game (default) |

Only one option can be selected. The value is stored in `GAME_MODE`.

## AI difficulty

After **Start**, if the mode is `"AI"` or `"AI_AUTO"`, an overlay on the empty board asks for Easy, Medium, or Hard. Manual mode skips this screen.

The choice is stored in `AI_DIFFICULTY` (default `"Easy"`). Confirming locks it in and starts play. Easy / Medium / Hard strategies are registered separately in `AI_STRATEGIES`.

## Sound effects

Clips from [Pixabay](https://pixabay.com/sound-effects/) are loaded once with `pygame.mixer` and play for both the player and the AI:

| Event | File |
| ----- | ---- |
| Safe cell revealed | `audio/reveal.mp3` |
| Flag placed | `audio/flagplace.mp3` |
| Mine opened | `audio/explosion.mp3` |
| Board cleared | `audio/win.mp3` |
