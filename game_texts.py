# game_texts.py

# Main menu
MENU_WELCOME = "Welcome to Texas Hold'em!"
MENU_OPTIONS = (
    "1. Play Game\n"
    "2. View Rules\n"
    "3. Quit"
)

GAME_MODE_OPTIONS = (
    "1. Player vs Player\n"
    "2. Player vs Computer\n"
    "3. Computer vs Computer\n"  
    )

MENU_PROMPT = "Select an option (1-3): "

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

# Betting prompts
PROMPT_CHECK_BET_FOLD = "Check (c), Bet (b), Fold (f)? "
PROMPT_CALL_RAISE_FOLD = "Call (c), Raise (r), Fold (f)? "
PROMPT_BET_AMOUNT = "Bet amount: "
PROMPT_RAISE_AMOUNT = "Raise amount: "
INVALID_ACTION = "Invalid action. Try again."
INVALID_BET = "Invalid bet amount."
INVALID_RAISE = "Invalid raise amount."

# Game messages
MSG_COMMUNITY_CARDS = "Community Cards:"
MSG_WINNER = "Winner(s):"
MSG_PLAYER_FOLDS = "{} folds."
MSG_PLAYER_WINS_FOLD = "{} wins the pot ({}) by everyone folding."
MSG_GAME_OVER = "Game Over! Winner: {}"

#Messages for debugging
MSG_SHUFFLED_DECK = "Shuffled Deck:"
MSG_HANDS = "Hands:"

# Chips / betting info
MSG_PLAYER_TURN = "{}'s turn. Chips: {}, To Call: {}, Pot: {}"
