import gameplay
import constants
from game_state import create_game_state

def main():
    #Create game state
    num_players = 2
    starting_chips = 1000

    game_state = create_game_state(
        num_players=num_players,
        starting_chips=starting_chips,
        small_blind=constants.STARTINGBLIND
    )

    #Build and shuffle deck
    game_state["deck"] = [
        r + s for s in constants.SUITS for r in constants.RANKS
    ]
    gameplay.shuffle_deck(game_state)

    # Debug
    print("Shuffled Deck:")
    print(game_state["deck"])

    #Deal cards
    gameplay.deal_cards(game_state)

    print("\nHands:")
    for player, data in game_state["players"].items():
        print(player, data["hand"])

    #Preflop betting
    gameplay.betting_phase(game_state)
    winner = gameplay.betting_phase(game_state)
    if winner:
        return

    #Flop
    gameplay.deal_flop(game_state)

    print("\nCommunity Cards:", game_state["community_cards"])
    gameplay.reset_bets(game_state)
    gameplay.betting_phase(game_state)
    winner = gameplay.betting_phase(game_state)
    if winner:
        return

    #Turn
    gameplay.deal_turnandriver(game_state)
    print("\nCommunity Cards:", game_state["community_cards"])
    gameplay.reset_bets(game_state)
    gameplay.betting_phase(game_state)
    winner = gameplay.betting_phase(game_state)
    if winner:
        return

    #River
    gameplay.deal_turnandriver(game_state)
    print("\nCommunity Cards:", game_state["community_cards"])
    gameplay.reset_bets(game_state)
    gameplay.betting_phase(game_state)
    winner = gameplay.betting_phase(game_state)
    if winner:
        return

    #Showdown
    evaluated = gameplay.evaluate_hands(game_state)
    winners = gameplay.determine_winner(evaluated)

    print("\nWinner(s):", winners)

if __name__ == "__main__":
    main()
