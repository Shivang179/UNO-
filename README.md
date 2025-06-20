# Terminal UNO Game (Python)

This is a simple terminal-based implementation of the classic **UNO** card game, featuring one human player versus an AI opponent. The game follows standard UNO rules and uses ANSI color codes to enhance the visual experience in the terminal.

---

## Features

- Play UNO against a basic AI opponent
- Fully functional card deck with action cards:
  - `SKIP`, `REVERSE`, `DRAW 2`
  - `WILD`, `WILD DRAW 4`
- Colored card display using ANSI escape codes
- Automatic reshuffling of the discard pile when deck is empty
- Support for declaring "UNO"
- AI decision-making based on basic strategy

---

## Requirements

- Python 3.x  
- Works in most Unix-based terminals and Windows command line (with ANSI support)

---

## How to Run

1. Save the game file as `uno_game.py`
2. Open your terminal or command prompt
3. Navigate to the directory containing the script
4. Run the game using:

```bash
python3 uno_game.py
