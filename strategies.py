import random
import game_texts
from gameplay import rank_hand

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

import random

def estimate_equity(game_state, player, simulations=500):
   
    hero_hand = game_state["players"][player]["hand"][:]
    community = game_state["community_cards"][:]
    full_deck = game_state["deck"][:]

    # Remove known cards from deck
    known_cards = hero_hand + community
    deck = [c for c in full_deck if c not in known_cards]

    opponents = [
        p for p in game_state["players"]
        if p != player and not game_state["players"][p]["folded"]
    ]

    wins = 0
    ties = 0

    for _ in range(simulations):
        sim_deck = deck[:]
        random.shuffle(sim_deck)

        # Complete board
        sim_board = community[:]
        while len(sim_board) < 5:
            sim_board.append(sim_deck.pop())

        # Give opponents random hands
        opp_hands = {}
        for opp in opponents:
            opp_hands[opp] = [sim_deck.pop(), sim_deck.pop()]

        # Evaluate hero
        hero_score = rank_hand(hero_hand + sim_board)

        best_score = hero_score
        winner_count = 1
        hero_is_best = True

        for opp in opponents:
            opp_score = rank_hand(opp_hands[opp] + sim_board)

            if opp_score > best_score:
                best_score = opp_score
                hero_is_best = False
                winner_count = 1
            elif opp_score == best_score:
                winner_count += 1

        if hero_is_best and winner_count == 1:
            wins += 1
        elif hero_is_best and winner_count > 1:
            ties += 1

    return (wins + ties * 0.5) / simulations

def monte_carlo_bot_strategy(game_state, player, legal_actions):

    if game_state["stage"] == "pre-flop":
        equity = estimate_equity(game_state, player, simulations=150)
    else:
        equity = estimate_equity(game_state, player, simulations=500)

    player_bet = game_state["players"][player]["bet"]
    current_bet = game_state["current_bet"]
    to_call = max(0, current_bet - player_bet)
    pot = game_state["pot"]
    chips = game_state["players"][player]["chips"]

    if to_call > 0:
        pot_odds = to_call / (pot + to_call)
    else:
        pot_odds = 0

    if equity > 0.65:
        if "raise" in legal_actions:
            min_raise = game_state["min_raise"]
           
            raise_amount = max(min_raise, min(pot // 2, chips))
            return "raise", raise_amount
        elif "bet" in legal_actions:
            bet_amount = max(game_state["min_raise"], min(pot // 2, chips))
            return "bet", bet_amount

    if "call" in legal_actions:
        if equity > pot_odds:
            return "call", None
        else:
            return "fold", None

    if "check" in legal_actions:
        if equity > 0.55 and "bet" in legal_actions:
            bet_amount = max(game_state["min_raise"], min(pot // 3, chips))
            return "bet", bet_amount
        return "check", None

    return "fold", None