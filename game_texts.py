# game_texts.py

# Main menu
MENU_WELCOME = "Welcome to Texas Hold'em!"
MENU_OPTIONS = (
    "1. Play Game\n"
    "2. View Stats\n"
    "3. Clear Stats\n"
    "4. View Rules\n"
    "5. Quit"
)

GAME_MODE_OPTIONS = (
    "1. Player vs Player\n"
    "2. Player vs Computer\n"
    "3. Computer vs Computer\n"  
    )

PLAYER_PROMPT = "Enter amount of players (2-8): "

MENU_PROMPT = "Select an option (1-5): "

# Rules
RULES_TEXT = """
Welcome to Texas Hold'em!

Rules:
1. Each player starts with equal chips.
2. Blinds are posted automatically each round.
3. Each player gets 2 private cards.
4. Community cards are dealt in stages:
   - Flop: 3 cards
   - Turn: 1 card
   - River: 1 card
5. Betting rounds happen pre-flop, post-flop, turn, and river.
6. Players can Check (c), Bet (b), Call (c), Raise (r), or Fold (f).
7. Minimum raise rules are enforced.
8. Showdown occurs if more than 1 player remains after the river.
9. Winner is determined by best hand ranking.

Have fun!
"""

INVALID = "Invalid input. Please try again."