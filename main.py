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
        dealer = game_state["player_order"][game_state["dealer_index"]]
        print(f"\n--- Hand {hand_number} ---")
        print(f"Dealer: {dealer}")

        gameplay.reset_round(game_state)
        gameplay.advance_dealer(game_state)
        play_round(game_state)
        print("\nChip Counts:")
        for p, d in game_state["players"].items():
            print(p, d["chips"])

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

    gameplay.post_blinds(game_state)

    print("\nHands:")
    for player, data in game_state["players"].items():
        if data["chips"] >= 0:
            print(player, data["hand"])

    if betting(game_state, reset=False):
        return
    
    active_not_allin = [
        p for p, d in game_state["players"].items()
        if not d["folded"] and not d["all_in"]
    ]

    if len(active_not_allin) == 0:
        # Everyone is all-in ? deal remaining streets
        remaining_stages = constants.STAGES[
            constants.STAGES.index(game_state["stage"]) + 1:
        ]

        for stage in remaining_stages:
            game_state["stage"] = stage
            if stage == "flop":
                gameplay.deal_flop(game_state)
            elif stage in ("turn", "river"):
                gameplay.deal_turnandriver(game_state)

        print("\nFinal Board:", game_state["community_cards"])

    for stage in constants.STAGES[1:]:
        game_state["stage"] = stage

        gameplay.reset_bets(game_state)

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
    split = game_state["pot"] // len(winners)

    for w in winners:
        game_state["players"][w]["chips"] += split

    print(f"Each winner receives {split}")
    game_state["pot"] = 0

    print("\nWinner(s):", winners)

def betting(game_state, reset=True):
    if reset:
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
