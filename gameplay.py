import random
from collections import Counter
from constants import RANK_VALUES, SUITS, RANKS

#Card Logic
# randomizes the deck of cards
def shuffle_deck(game_state):
    game_state["deck"] = [
        r + s for s in SUITS for r in RANKS
    ]
    random.shuffle(game_state["deck"])

def reset_round(game_state):
    game_state["deck"] = [
        r + s for s in SUITS for r in RANKS
    ]
    shuffle_deck(game_state)

    game_state["community_cards"] = []
    game_state["pot"] = 0
    game_state["current_bet"] = 0

    for data in game_state["players"].values():
        data["hand"] = []
        data["bet"] = 0
        data["folded"] = False

# deals two cards to each player
def deal_cards(game_state):
    for _ in range(2):
        for player, data in game_state["players"].items():
            if data["chips"] > 0:
                data["hand"].append(game_state["deck"].pop(0))
        
# deals the flop (three community cards)
def deal_flop(game_state):
     game_state["deck"].pop(0)                 
     for _ in range(3):
         game_state["community_cards"].append(
             game_state["deck"].pop(0)
         )

 # deals the turn or river (one community card)
def deal_turnandriver(game_state):
    game_state["deck"].pop(0)
    game_state["community_cards"].append(
        game_state["deck"].pop(0)
    )

def is_straight(values):
    values = sorted(set(values), reverse=True)

    # Ace-low straight (A,2,3,4,5)
    if values == [14, 5, 4, 3, 2]:
        return True, 5

    for i in range(len(values) - 4):
        window = values[i:i+5]
        if window[0] - window[4] == 4:
            return True, window[0]

    return False, None

def rank_hand(cards):
    ranks = [card[:-1] for card in cards]
    suits = [card[-1] for card in cards]

    values = [RANK_VALUES[r] for r in ranks]

    rank_counts = Counter(values)
    suit_counts = Counter(suits)

    counts = sorted(rank_counts.values(), reverse=True)

    # Flush
    flush_suit = None
    for suit, count in suit_counts.items():
        if count >= 5:
            flush_suit = suit
            break

    # Straight
    is_str, high_straight = is_straight(values)

    # Straight flush
    if flush_suit:
        flush_cards = [
            RANK_VALUES[c[0]] for c in cards if c[1] == flush_suit
        ]
        sf, high_sf = is_straight(flush_cards)
        if sf:
            return (8, high_sf)

    # Four of a kind
    if 4 in counts:
        four = max(v for v, c in rank_counts.items() if c == 4)
        return (7, four)

    # Full house
    if 3 in counts and 2 in counts:
        triple = max(v for v, c in rank_counts.items() if c == 3)
        pair = max(v for v, c in rank_counts.items() if c == 2)
        return (6, triple, pair)

    # Flush
    if flush_suit:
        high_flush = max(
            RANK_VALUES[c[0]] for c in cards if c[1] == flush_suit
        )
        return (5, high_flush)

    # Straight
    if is_str:
        return (4, high_straight)

    # Three of a kind
    if 3 in counts:
        triple = max(v for v, c in rank_counts.items() if c == 3)
        return (3, triple)

    # Two pair
    if counts.count(2) >= 2:
        pairs = sorted([v for v, c in rank_counts.items() if c == 2], reverse=True)
        return (2, pairs[0], pairs[1])

    # One pair
    if 2 in counts:
        pair = max(v for v, c in rank_counts.items() if c == 2)
        return (1, pair)
    
    # High card
    return (0, max(values))

def evaluate_hands(game_state):
    evaluated = {}
    for player, data in game_state["players"].items():
        full_hand = data["hand"] + game_state["community_cards"]
        evaluated[player] = rank_hand(full_hand)
    return evaluated

def determine_winner(evaluated_hands):
    best_rank = max(evaluated_hands.values())
    winners = [
        player for player, rank in evaluated_hands.items()
        if rank == best_rank
    ]
    return winners

# Betting Logic  

def reset_bets(game_state):
    game_state["current_bet"] = 0
    for player in game_state["players"].values():
        player["bet"] = 0

def check_fold_win(game_state):
    active_players = [
        p for p, data in game_state["players"].items()
        if not data["folded"]
    ]

    if len(active_players) == 1:
        winner = active_players[0]
        game_state["players"][winner]["chips"] += game_state["pot"]

        print(f"\n{winner} wins the pot ({game_state['pot']}) by everyone folding.")
        game_state["pot"] = 0
        return winner

    return None
def betting_phase(game_state):
    print("\n--- Betting Phase ---")
    
    game_state["last_raiser"] = None

    while True:
        active_players = [
            p for p, d in game_state["players"].items()
            if not d["folded"] and d["chips"] > 0
        ]

        for player in active_players:
            data = game_state["players"][player]

            # Skip if already matched the bet
            if data["bet"] == game_state["current_bet"] > 0 and data["bet"] == game_state["current_bet"]:
                continue

            to_call = game_state["current_bet"] - data["bet"]

            print(f"{player}'s turn. Chips: {data['chips']}, To Call: {to_call}, Pot: {game_state['pot']}")

            if to_call == 0:
                action = input("Check (c), Bet (b), Fold (f)? ").lower()
            else:
                action = input("Call (c), Raise (r), Fold (f)? ").lower()

            if action == 'f':
                data["folded"] = True
                print(f"{player} folds.")

                winner = check_fold_win(game_state)
                if winner:
                    return winner

            elif action == 'c' and to_call > 0:
                bet_amount = min(to_call, data["chips"])
                data["chips"] -= bet_amount
                data["bet"] += bet_amount
                game_state["pot"] += bet_amount
                print(f"{player} calls {bet_amount}.")

            elif action == 'c' and to_call == 0:
                print(f"{player} checks.")

            elif action == 'b' and game_state["current_bet"] == 0:
                amount = int(input("Bet amount: "))
                if amount <= 0 or amount > data["chips"]:
                    print("Invalid bet amount.")
                    continue

                data["chips"] -= amount
                data["bet"] += amount
                game_state["pot"] += amount
                game_state["current_bet"] = amount
                game_state["last_raiser"] = player
                print(f"{player} bets {amount}.")

            elif action == 'r' and game_state["current_bet"] > 0:
                amount = int(input("Raise amount: "))
                if amount <= 0 or (to_call + amount) > data["chips"]:
                    print("Invalid raise amount.")
                    continue

                total = to_call + amount
                data["chips"] -= total
                data["bet"] += total
                game_state["pot"] += total
                game_state["current_bet"] = data["bet"]
                game_state["last_raiser"] = player
                print(f"{player} raises to {data['bet']}.")

            else:
                print("Invalid action. Try again.")
                continue

        # End betting round if everyone checked
        if game_state["last_raiser"] is None:
            break

        # End betting round if all active players have matched the bet
        if all(
            game_state["players"][p]["bet"] == game_state["current_bet"]
            or game_state["players"][p]["folded"]
            for p in active_players
        ):
            break




    return None 