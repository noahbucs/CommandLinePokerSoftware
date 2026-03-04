import gameplay
import constants
from game_state import create_game_state
import strategies
import menu
import game_texts

def main(mode):
    #Create game state
    num_players = None
    starting_chips = 1000
    hand_number = 1

    while num_players is None:
        num_players = input(game_texts.PLAYER_PROMPT)
        if num_players.isdigit() and 2 <= int(num_players) <= 8:
            num_players = int(num_players)
        else:
            print(game_texts.INVALID)
            num_players = None

    game_state = create_game_state(
        num_players=num_players,
        starting_chips=starting_chips,
        small_blind=constants.STARTINGBLIND
    )
    
    players = list(game_state["players"].keys())

    if mode == "1":  # Player vs Player
        for p in players:
            game_state["players"][p]["strategy"] = strategies.human_strategy

    elif mode == "2":  # Player vs Computer
        for p in players:
            if p == players[0]:
                game_state["players"][p]["strategy"] = strategies.human_strategy
            else:
                game_state["players"][p]["strategy"] = strategies.monte_carlo_bot_strategy
       
    elif mode == "3":  # Computer vs Computer
        for p in players:
            game_state["players"][p]["strategy"] = strategies.monte_carlo_bot_strategy

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

        over, active_players_remaining = game_over(game_state)
        if over:
            print(f"\nGame Over! Winner: {active_players_remaining[0]}")
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
        mode = menu.show_main_menu()

        if mode is None:
            break

        main(mode)

        again = input("\nPlay again? (y/n): ").strip().lower()
        while again not in ["y", "n"]:
            again = input("Please enter y or n: ").strip().lower()
            if again != "y":
                print("Thanks for playing!")
                break