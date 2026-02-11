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
        data["all_in"] = False

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

def advance_dealer(game_state):
    players = game_state["player_order"]
    num_players = len(players)

    while True:
        game_state["dealer_index"] = (game_state["dealer_index"] + 1) % num_players
        dealer = players[game_state["dealer_index"]]
        if game_state["players"][dealer]["chips"] > 0:
            break

def get_action_order(game_state, stage):
    players = game_state["player_order"]
    active_players = [
        p for p in players if game_state["players"][p]["chips"] > 0 and not game_state["players"][p]["folded"]
    ]

    dealer = game_state["dealer_index"]
    num_players = len(active_players)

    # Heads up logic
    if num_players == 2:
        if stage == "preflop":
            start_index = dealer  # dealer acts first
        else:
            start_index = (dealer + 1) % len(players)  # non-dealer first
    else:
        if stage == "preflop":
            start_index = (dealer + 3) % len(players)
        else:
            start_index = (dealer + 1) % len(players)

    order = []
    for i in range(len(players)):
        player = players[(start_index + i) % len(players)]
        if player in active_players:
            order.append(player)

    return order


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
def post_blinds(game_state):
    players = game_state["player_order"]
    active_players = [
        p for p in players if game_state["players"][p]["chips"] > 0
    ]

    dealer = game_state["dealer_index"]

    # Heads up special case: dealer is small blind, other is big blind
    if len(active_players) == 2:
        sb_player = players[dealer]
        bb_player = players[(dealer + 1) % len(players)]
    else:
        sb_player = players[(dealer + 1) % len(players)]
        bb_player = players[(dealer + 2) % len(players)]

    sb_amount = min(game_state["small_blind"], game_state["players"][sb_player]["chips"])
    bb_amount = min(game_state["big_blind"], game_state["players"][bb_player]["chips"])

    # Post blinds
    game_state["players"][sb_player]["chips"] -= sb_amount
    game_state["players"][sb_player]["bet"] += sb_amount
    game_state["pot"] += sb_amount

    game_state["players"][bb_player]["chips"] -= bb_amount
    game_state["players"][bb_player]["bet"] += bb_amount
    game_state["pot"] += bb_amount

    game_state["current_bet"] = bb_amount
    game_state["last_raiser"] = bb_player

    print(f"{sb_player} posts small blind ({sb_amount})")
    print(f"{bb_player} posts big blind ({bb_amount})")


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

    if game_state["stage"] != "preflop":
        game_state["last_raiser"] = None

    players_acted = set()

    while True:
        action_order = get_action_order(game_state, game_state["stage"])

        for player in action_order:
            data = game_state["players"][player]

            # Skip folded players
            if data["folded"] or data ["all_in"]:
                continue

            to_call = game_state["current_bet"] - data["bet"]

            print(f"{player}'s turn. Chips: {data['chips']}, To Call: {to_call}, Pot: {game_state['pot']}")

            # Determine available actions
            if to_call == 0:
                action = input("Check (c), Bet (b), Fold (f)? ").lower()
            else:
                action = input("Call (c), Raise (r), Fold (f)? ").lower()

            #Fold
            if action == 'f':
                data["folded"] = True
                print(f"{player} folds.")

                winner = check_fold_win(game_state)
                if winner:
                    return winner

            #Call
            elif action == 'c' and to_call > 0:
                bet_amount = min(to_call, data["chips"])
                data["chips"] -= bet_amount
                data["bet"] += bet_amount
                game_state["pot"] += bet_amount
                print(f"{player} calls {bet_amount}.")
                if data["chips"] == 0:
                    data["all_in"] = True
                    print(f"{player} goes all-in")

            #Checking
            elif action == 'c' and to_call == 0:
                print(f"{player} checks.")

            #Betting
            elif action == 'b' and game_state["current_bet"] == 0:
                try:
                    amount = int(input("Bet amount: "))
                except ValueError:
                    print("Invalid input.")
                    continue

                if amount <= 0 or amount > data["chips"]:
                    print("Invalid bet amount.")
                    continue

                data["chips"] -= amount
                if data["chips"] == 0:
                    data["all_in"] = True
                    print(f"{player} goes all-in")
                data["bet"] += amount
                game_state["pot"] += amount
                game_state["current_bet"] = amount
                game_state["min_raise"] = amount
                game_state["last_raiser"] = player
                players_acted = {player}

                print(f"{player} bets {amount}.")
                continue  # restart loop after bet

            #Raise
            elif action == 'r' and game_state["current_bet"] > 0:
                while True:
                    try:
                        raise_amount = int(input("Raise amount: "))
                    except ValueError:
                        print("Enter a valid number.")
                        continue

                    if raise_amount < game_state["min_raise"]:
                        print(f"Minimum raise is {game_state['min_raise']}.")
                        continue

                    if raise_amount + to_call > data["chips"]:
                        print("Not enough chips.")
                        continue

                    break

                total = to_call + raise_amount
                data["chips"] -= total
                if data["chips"] == 0:
                    data["all_in"] = True
                    print(f"{player} goes all-in")
                data["bet"] += total
                game_state["pot"] += total
                game_state["current_bet"] = data["bet"]
                game_state["min_raise"] = raise_amount
                game_state["last_raiser"] = player
                players_acted = {player}

                print(f"{player} raises to {data['bet']}.")
                continue  # restart loop after raise

            else:
                print("Invalid action.")
                continue

            players_acted.add(player)

        active_players = [
            p for p in game_state["players"]
            if not game_state["players"][p]["folded"]
        ]

        #All in stop
        active_not_allin = [
            p for p, d in game_state["players"].items()
            if not d["folded"] and not d["all_in"]
        ]

        # If 0 or 1 players can still act, betting ends
        if len(active_not_allin) <= 1:
            break

        # All active players have matched the current bet
        bets_equal = all(
            game_state["players"][p]["bet"] == game_state["current_bet"]
            for p in active_players
        )

        # If no raises happened and everyone acted once
        # If no raises happened and eveyone acted once
        if game_state["last_raiser"] is None and bets_equal:
            break

        # If there was a raise and action returned to raiser
        if (
            game_state["last_raiser"] is not None
            and len(players_acted) == len(active_players)
            and bets_equal
        ):
            break

    return None