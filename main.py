import gameplay
import constants
from game_state import create_game_state
import strategies
import menu


def get_bot_strategy(difficulty):
    if difficulty == "easy":
        return strategies.easy_bot_strategy
    elif difficulty == "medium":
        return strategies.medium_bot_strategy
    elif difficulty == "hard":
        return strategies.monte_carlo_bot_strategy
    else:
        return strategies.random_bot_strategy


def main(settings):

    num_players = settings["players"]
    mode = settings["mode"]
    difficulty = settings.get("difficulty")

    starting_chips = 1000
    hand_number = 1

    game_state = create_game_state(
        num_players=num_players,
        starting_chips=starting_chips,
        small_blind=constants.STARTINGBLIND
    )

    players = list(game_state["players"].keys())

    if mode == "pvp":
        for p in players:
            game_state["players"][p]["strategy"] = strategies.human_strategy

    elif mode == "pvc":
        for p in players:
            if p == players[0]:
                game_state["players"][p]["strategy"] = strategies.human_strategy
            else:
                game_state["players"][p]["strategy"] = get_bot_strategy(difficulty)

    elif mode == "cvc":
        for p in players:
            game_state["players"][p]["strategy"] = get_bot_strategy(difficulty)

        game_state["verbose"] = False

    while True:

        dealer = game_state["player_order"][game_state["dealer_index"]]

        print(f"\n--- Hand {hand_number} ---")
        print(f"Dealer: {dealer}")

        gameplay.reset_round(game_state)
        gameplay.advance_dealer(game_state)
        gameplay.play_round(game_state)

        game_state["stats"].flush_hand()

        print("\nChip Counts:")
        for p, d in game_state["players"].items():
            print(p, d["chips"])

        over, active_players = game_over(game_state)

        if over:
            print(f"\nGame Over! Winner: {active_players[0]}")
            game_state["stats"].print_stats()
            break

        hand_number += 1


def game_over(game_state):

    active = [
        p for p, d in game_state["players"].items()
        if d["chips"] > 0
    ]

    return len(active) == 1, active


if __name__ == "__main__":

    while True:

        settings = menu.show_main_menu()

        if settings is None:
            break

        main(settings)

        if not menu.play_again():
            print("Thanks for playing!")
            break