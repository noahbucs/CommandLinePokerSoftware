# Main menu

MENU_WELCOME = "Welcome to Texas Hold'em!"

MENU_OPTIONS = (
    "1. Play Game\n"
    "2. View Stats\n"
    "3. Clear Stats\n"
    "4. View Rules\n"
    "5. Quit"
)

MENU_PROMPT = "Select an option (1-5): "

# Game mode selection
GAME_MODE_OPTIONS = (
    "1. Player vs Player\n"
    "2. Player vs Computer\n"
    "3. Computer vs Computer\n"
)

PLAYER_PROMPT = "Enter amount of players (2-8): "


# Bot difficulty

BOT_DIFFICULTY_PROMPT = (
    "\nSelect bot difficulty:\n"
    "1. Easy\n"
    "2. Medium\n"
    "3. Hard\n"
    "4. Chaos\n"
)


# Rules text

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
5. Betting rounds occur pre-flop, flop, turn, and river.
6. Players may check, bet, call, raise, or fold.
7. Minimum raise rules apply.
8. Showdown occurs if multiple players remain after the river.
9. The best 5-card poker hand wins.

Have fun!
"""

# Error messages
INVALID = "Invalid input. Please try again."