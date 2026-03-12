import random
#import time 
from collections import Counter
from constants import RANK_VALUES, SUITS, RANKS , STAGES
from itertools import combinations

#Card Logic
#Randomizes the deck of cards
def shuffle_deck(game_state):
    game_state["deck"] = [
        r + s for s in SUITS for r in RANKS
    ]
    random.shuffle(game_state["deck"])

#resets everything back to default
def reset_round(game_state):
    game_state["deck"] = [
        r + s for s in SUITS for r in RANKS
    ]
    shuffle_deck(game_state)

    game_state["stage"] = "preflop"
    game_state["community_cards"] = []
    game_state["pot"] = 0
    game_state["current_bet"] = 0
    game_state["min_raise"] = game_state["big_blind"]

    for p in game_state["players"]:
        game_state["players"][p]["bet"] = 0
        game_state["players"][p]["folded"] = False
        game_state["players"][p]["all_in"] = False  

    for data in game_state["players"].values():
        data["hand"] = []
        data["bet"] = 0
        data["folded"] = False
        data["all_in"] = False
        data["total_contributed"] = 0

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

#deals the turn or river (one community card)
def deal_turnandriver(game_state):
    game_state["deck"].pop(0)
    game_state["community_cards"].append(
        game_state["deck"].pop(0)
    )

#Changes the dealer to the next player
def advance_dealer(game_state):
    players = game_state["player_order"]
    num_players = len(players)

    while True:
        game_state["dealer_index"] = (game_state["dealer_index"] + 1) % num_players
        dealer = players[game_state["dealer_index"]]
        if game_state["players"][dealer]["chips"] > 0:
            break

# Gets the order of the players
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

#Helper to check valid actions
def get_legal_actions(game_state, player):
    data = game_state["players"][player]
    to_call = max(0, game_state["current_bet"] - data["bet"])

    if data["chips"] <= 0:
        return []

    if to_call == 0:
        return ["check", "bet", "fold"]
    else:
        return ["call", "raise", "fold"]

#Gives each hand a score
def rank_hand(cards):
    best = None

    # Check all 5-card combinations from 7 cards
    for combo in combinations(cards, 5):
        score = rank_five_card_hand(combo)
        if best is None or score > best:
            best = score

    return best

#Ranks hand based off best 5 cards
def rank_five_card_hand(cards):
    ranks = [card[:-1] for card in cards]
    suits = [card[-1] for card in cards]

    values = sorted([RANK_VALUES[r] for r in ranks], reverse=True)
    rank_counts = Counter(values)
    suit_counts = Counter(suits)

    counts = sorted(rank_counts.values(), reverse=True)

    # Detect flush
    is_flush = max(suit_counts.values()) == 5

    # Detect straight
    unique_vals = sorted(set(values), reverse=True)

    # Wheel straight (A-2-3-4-5)
    if unique_vals == [14, 5, 4, 3, 2]:
        is_straight = True
        straight_high = 5
    else:
        is_straight = len(unique_vals) == 5 and unique_vals[0] - unique_vals[-1] == 4
        straight_high = unique_vals[0] if is_straight else None

    # Straight Flush
    if is_straight and is_flush:
        return (8, straight_high)

    # Four of a kind
    if 4 in counts:
        four = max(v for v, c in rank_counts.items() if c == 4)
        kicker = max(v for v, c in rank_counts.items() if c == 1)
        return (7, four, kicker)

    # Full house
    if counts == [3, 2]:
        triple = max(v for v, c in rank_counts.items() if c == 3)
        pair = max(v for v, c in rank_counts.items() if c == 2)
        return (6, triple, pair)

    # Flush
    if is_flush:
        return (5, *values)

    # Straight
    if is_straight:
        return (4, straight_high)

    # Three of a kind
    if 3 in counts:
        triple = max(v for v, c in rank_counts.items() if c == 3)
        kickers = sorted([v for v, c in rank_counts.items() if c == 1], reverse=True)
        return (3, triple, *kickers)

    # Two pair
    if counts == [2, 2, 1]:
        pairs = sorted([v for v, c in rank_counts.items() if c == 2], reverse=True)
        kicker = max(v for v, c in rank_counts.items() if c == 1)
        return (2, pairs[0], pairs[1], kicker)

    # One pair
    if counts == [2, 1, 1, 1]:
        pair = max(v for v, c in rank_counts.items() if c == 2)
        kickers = sorted([v for v, c in rank_counts.items() if c == 1], reverse=True)
        return (1, pair, *kickers)

    # High card
    return (0, *values)

def evaluate_hands(game_state):
    evaluated = {}
    for player, data in game_state["players"].items():
        full_hand = data["hand"] + game_state["community_cards"]
        evaluated[player] = rank_hand(full_hand)
    return evaluated

def resolve_showdown(game_state):
    players = game_state["players"]
    side_pots = game_state.get("side_pots", [])
    stats = game_state["stats"]

    # Evaluate all hands once
    hand_strengths = evaluate_hands(game_state)

    # Resolve each pot independently
    for pot in side_pots:
        eligible = [
            p for p in pot["eligible"]
            if not players[p]["folded"]
        ]

        if not eligible:
            continue

        best = max(hand_strengths[p] for p in eligible)

        winners = [
            p for p in eligible
            if hand_strengths[p] == best
        ]

        split_amount = pot["amount"] // len(winners)

        for w in winners:
            players[w]["chips"] += split_amount
            game_state["stats"].record_win(w, split_amount)

        for p in eligible:
            won = p in winners
            stats.record_showdown(p, won)

        print(f"Side pot {pot['amount']} won by {winners}")

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
    for p, amount in [(sb_player, sb_amount), (bb_player, bb_amount)]:
        game_state["players"][p]["chips"] -= amount
        game_state["players"][p]["bet"] += amount
        game_state["pot"] += amount
        game_state["stats"].record_action(p, "blind", "preflop")
        if game_state["players"][p]["chips"] == 0:
            game_state["players"][p]["all_in"] = True

    if sb_amount > bb_amount:
        excess = sb_amount - bb_amount
        game_state["players"][sb_player]["chips"] += excess
        game_state["players"][sb_player]["bet"] -= excess
        game_state["pot"] -= excess
        if game_state["players"][sb_player]["all_in"]:
            game_state["players"][sb_player]["all_in"] = False

    game_state["current_bet"] = bb_amount
    game_state["last_raiser"] = bb_player

    print(f"{sb_player} posts small blind ({sb_amount})")
    print(f"{bb_player} posts big blind ({bb_amount})")

def reset_bets(game_state):
    game_state["current_bet"] = 0
    for player in game_state["players"].values():
        # Carry forward what was bet this street into the running total
        player["total_contributed"] = player.get("total_contributed", 0) + player["bet"]
        player["bet"] = 0

def check_fold_win(game_state):
    active_players = [
        p for p, data in game_state["players"].items()
        if not data["folded"]
    ]

    if len(active_players) == 1:
        winner = active_players[0]
        pot = game_state["pot"]
        game_state["players"][winner]["chips"] += pot
        print(f"\n{winner} wins the pot ({pot}) by everyone folding.")
        game_state["pot"] = 0
        return winner, pot

    return None, 0

def build_side_pots(game_state):
    players = game_state["players"]

    contributions = {
        p: players[p].get("total_contributed", 0) + players[p]["bet"]
        for p in players
        if players[p].get("total_contributed", 0) + players[p]["bet"] > 0
    }

    side_pots = []

    while contributions:
        # Smallest contribution remaining
        min_bet = min(contributions.values())

        # Players eligible for this layer
        eligible = list(contributions.keys())

        pot_amount = min_bet * len(eligible)

        side_pots.append({
            "amount": pot_amount,
            "eligible": eligible.copy()
        })

        # Subtract layer from each player
        to_remove = []
        for p in contributions:
            contributions[p] -= min_bet
            if contributions[p] == 0:
                to_remove.append(p)

        for p in to_remove:
            del contributions[p]

    game_state["side_pots"] = side_pots

def all_players_all_in_or_folded(game_state):
    active = [
        p for p, d in game_state["players"].items()
        if not d["folded"]
    ]

    not_all_in = [
        p for p in active
        if not game_state["players"][p]["all_in"]
    ]

    return len(not_all_in) <= 1

# If we hit an all-in situation where betting is effectively over, run out the rest of the cards and resolve showdown immediately
def runout_and_showdown(game_state):
    current_index = STAGES.index(game_state["stage"])
    remaining = STAGES[current_index + 1:]

    for stage in remaining:
        game_state["stage"] = stage
        if stage == "flop":
            deal_flop(game_state)
        else:
            deal_turnandriver(game_state)

    while len(game_state["community_cards"]) < 5:
        game_state["community_cards"].append(game_state["deck"].pop())

    print("\nFinal Board:", game_state["community_cards"])

    build_side_pots(game_state)
    resolve_showdown(game_state)

    cleanup_after_hand(game_state)
# After a hand is fully resolved, reset pot and bets but keep chips and stats intact for next hand
def cleanup_after_hand(game_state):
    game_state["pot"] = 0
    for p in game_state["players"]:
        game_state["players"][p]["bet"] = 0

def play_round(game_state):
    #print("Shuffled Deck:")
    #print(game_state["deck"])

    game_state["stats"].record_new_hand()

    deal_cards(game_state)
    post_blinds(game_state)

    #print("\nHands:")
    #for player, data in game_state["players"].items():
        #print(player, data["hand"])

    #preflop
    result = betting_phase(game_state)
    if result == "fold_win":
        return  # fold win
    if result == "all_in_runout":
        runout_and_showdown(game_state)
        return

    # Check if betting is permanently over (all-in situation)
    if all_players_all_in_or_folded(game_state):
        runout_and_showdown(game_state)
        return

    #flop,turn, river
    for stage in ["flop", "turn", "river"]:
        game_state["stage"] = stage
        reset_bets(game_state)

        if stage == "flop":
            deal_flop(game_state)
        else:
            deal_turnandriver(game_state)

        print("\nCommunity Cards:", game_state["community_cards"])

        result = betting_phase(game_state)
        if result == "fold_win":
            return
        if result == "all_in_runout":
            runout_and_showdown(game_state)
            return

        if all_players_all_in_or_folded(game_state):
            runout_and_showdown(game_state)
            return

    #Showdown
    build_side_pots(game_state)
    resolve_showdown(game_state)

    cleanup_after_hand(game_state)

def betting(game_state, reset=True):
    if reset:
        reset_bets(game_state)

    winner = betting_phase(game_state)
    if winner:
        return winner

def betting_phase(game_state):
    print("\n--- Betting Phase ---")

    stats = game_state["stats"]

    if game_state["stage"] == "preflop":
        players = game_state["player_order"]
        dealer = game_state["dealer_index"]
        active_players_list = [
            p for p in players if game_state["players"][p]["chips"] > 0 and not game_state["players"][p]["folded"]
        ]
        if len(active_players_list) == 2:
            bb_player = players[(dealer + 1) % len(players)]
        else:
            bb_player = players[(dealer + 2) % len(players)]
        players_acted = {bb_player}
        last_raiser = game_state.get("last_raiser")
    else:
        game_state["last_raiser"] = None
        players_acted = set()
        last_raiser = None

    while True:
        action_order = get_action_order(game_state, game_state["stage"])
        acted_this_pass = False

        for player in action_order:
            data = game_state["players"][player]

            if data["folded"] or data["all_in"]:
                continue

            if player in players_acted:
                to_call_check = game_state["current_bet"] - data["bet"]
                if to_call_check == 0:
                    continue

            to_call = max(0, game_state["current_bet"] - data["bet"])
            chips = data["chips"]

            if game_state.get("verbose", True):
                print(f"\n{player}'s turn")
                print(f"Stage: {game_state['stage']}")
                print(f"Community Cards: {game_state['community_cards']}")
                print(f"Your Hand: {data['hand']}")
                print(f"Chips: {chips}")
                print(f"Current Bet: {game_state['current_bet']}")
                print(f"Your Bet: {data['bet']}")
                print(f"To Call: {to_call}")
                print(f"Pot: {game_state['pot']}")

            legal_actions = get_legal_actions(game_state, player)
            if not legal_actions:
                continue

            strategy = data["strategy"]
            action, amount = strategy(game_state, player, legal_actions)

            acted_this_pass = True

            #Fold
            if action == "fold":
                data["folded"] = True
                print(f"{player} folds.")
                stats.record_action(player, "fold", game_state["stage"])

                winner, pot = check_fold_win(game_state)
                if winner:
                    stats.record_win(winner, pot)
                    return "fold_win"

                players_acted.add(player)

            #Check
            elif action == "check":
                print(f"{player} checks.")
                stats.record_action(player, "check", game_state["stage"])
                players_acted.add(player)

            #Call
            elif action == "call":
                call_amount = min(to_call, chips)

                data["chips"] -= call_amount
                data["bet"] += call_amount
                game_state["pot"] += call_amount

                print(f"{player} calls {call_amount}.")
                stats.record_action(player, "call", game_state["stage"])
                players_acted.add(player)

                if data["chips"] == 0:
                    data["all_in"] = True
                    print(f"{player} goes all-in.")

            #All-in
            elif action == "all-in":
                all_in_amount = chips

                data["bet"] += all_in_amount
                game_state["pot"] += all_in_amount
                data["chips"] = 0
                data["all_in"] = True

                print(f"{player} goes all-in for {all_in_amount}.")
                stats.record_action(player, "all-in", game_state["stage"])

                if data["bet"] > game_state["current_bet"]:
                    raise_size = data["bet"] - game_state["current_bet"]
                    game_state["min_raise"] = raise_size
                    game_state["current_bet"] = data["bet"]
                    game_state["last_raiser"] = player
                    players_acted = {player}

            #Bet
            elif action == "bet":
                bet_amount = min(amount, chips)

                data["chips"] -= bet_amount
                data["bet"] += bet_amount
                game_state["pot"] += bet_amount

                game_state["current_bet"] = data["bet"]
                game_state["min_raise"] = bet_amount
                game_state["last_raiser"] = player
                players_acted = {player}

                print(f"{player} bets {bet_amount}.")
                stats.record_action(player, "bet", game_state["stage"])

                if data["chips"] == 0:
                    data["all_in"] = True
                    print(f"{player} goes all-in.")

            #Raise
            elif action == "raise":
                raise_increment = amount

                if raise_increment < game_state["min_raise"]:
                    call_amount = min(to_call, chips)
                    data["chips"] -= call_amount
                    data["bet"] += call_amount
                    game_state["pot"] += call_amount
                    print(f"{player} calls {call_amount}.")
                    stats.record_action(player, "call", game_state["stage"])
                    players_acted.add(player)
                    if data["chips"] == 0:
                        data["all_in"] = True
                        print(f"{player} goes all-in.")
                    continue

                total_needed = to_call + raise_increment
                total_needed = min(total_needed, chips)

                data["chips"] -= total_needed
                data["bet"] += total_needed
                game_state["pot"] += total_needed

                print(f"{player} raises to {data['bet']}.")
                stats.record_action(player, "raise", game_state["stage"])

                if data["bet"] > game_state["current_bet"]:
                    raise_size = data["bet"] - game_state["current_bet"]
                    game_state["min_raise"] = raise_size
                    game_state["current_bet"] = data["bet"]
                    game_state["last_raiser"] = player
                    players_acted = {player}

                if data["chips"] == 0:
                    data["all_in"] = True
                    print(f"{player} goes all-in.")

        active_players = [
            p for p in game_state["players"]
            if not game_state["players"][p]["folded"]
        ]

        active_not_allin = [
            p for p in active_players
            if not game_state["players"][p]["all_in"]
        ]

        if len(active_not_allin) <= 1:
            return "all_in_runout"

        bets_equal = all(
            game_state["players"][p]["bet"] == game_state["current_bet"]
            for p in active_not_allin
        )

        if bets_equal and all(p in players_acted for p in active_not_allin):
            break

        if not acted_this_pass:
            break

    return None