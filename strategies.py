import random
import game_texts

def human_strategy(game_state, player, legal_actions):
    print(f"\n{player}'s turn.")
    print("Legal actions:", legal_actions)

    action = input("Choose action: ").lower()

    while action not in legal_actions:
        action = input(game_texts.INVALID).lower()

    if action in ["bet", "raise"]:
        amount = int(input("Amount: "))
        return action, amount

    return action, None

def random_bot_strategy(game_state, player, legal_actions):
    chips = game_state["players"][player]["chips"]
    min_raise = game_state.get("min_raise", 0)

    action = random.choice(legal_actions)

    if action in ["bet", "raise"]:

        if chips <= 0:
            return "check" if "check" in legal_actions else "fold", None

        if chips < min_raise:
            if "call" in legal_actions:
                return "call", None
            elif "check" in legal_actions:
                return "check", None
            else:
                return "fold", None

        amount = random.randint(min_raise, chips)
        return action, amount

    return action, None