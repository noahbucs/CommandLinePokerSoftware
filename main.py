import gameplay
import constants
from game_state import create_game_state

def main():
    #Create game state
    num_players = 2
    starting_chips = 1000
    hand_number = 1

    game_state = create_game_state(
        num_players=num_players,
        starting_chips=starting_chips,
        small_blind=constants.STARTINGBLIND
    )

    while True:
        print(f"\n--- Hand {hand_number} ---")

        gameplay.reset_round(game_state)
        play_round(game_state)

        over, active_players_remaining = game_over(game_state)
        if over:
            print(f"\nGame Over! Winner: {active_players_remaining[0]}")
            break
    
        hand_number += 1

def play_round(game_state):
    # Debug
    print("Shuffled Deck:")
    print(game_state["deck"])

    #Deal cards
    gameplay.deal_cards(game_state)

    print("\nHands:")
    for player, data in game_state["players"].items():
        if data["chips"] <= 0:
            print(player, data["hand"])

    #Preflop betting
    if betting(game_state):
        return

    for stage in constants.STAGES:

        if stage == "flop":
            gameplay.deal_flop(game_state)
        elif stage in ("turn", "river"):
            gameplay.deal_turnandriver(game_state)

        if stage != "preflop":
            print("\nCommunity Cards:", game_state["community_cards"])

        if betting(game_state):
            return

    #Showdown
    evaluated = gameplay.evaluate_hands(game_state)
    winners = gameplay.determine_winner(evaluated)

    print("\nWinner(s):", winners)

def betting(game_state):
    gameplay.reset_bets(game_state)
    winner = gameplay.betting_phase(game_state)
    if winner:
        return winner

def game_over(game_state):
    active = [
        p for p, d in game_state["players"].items()
        if d["chips"] > 0
    ]
    return len(active) == 1, active

if __name__ == "__main__":
    main()
