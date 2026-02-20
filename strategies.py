import random

def human_strategy(game_state, player, legal_actions):
    print(f"\n{player}'s turn.")
    print("Legal actions:", legal_actions)

    action = input("Choose action: ").lower()

    while action not in legal_actions:
        action = input("Invalid. Choose again: ").lower()

    if action in ["bet", "raise"]:
        amount = int(input("Amount: "))
        return action, amount

    return action, None

def random_bot_strategy(game_state, player, legal_actions):
    action = random.choice(legal_actions)

    if action in ["bet", "raise"]:
        min_raise = game_state["min_raise"]
        chips = game_state["players"][player]["chips"]
        amount = random.randint(min_raise, chips)
        return action, amount

    return action, None