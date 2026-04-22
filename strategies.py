import constants
import game_texts
import random
from collections import defaultdict, Counter
from gameplay import rank_hand

# Simple LRU cache implementation for equity simulation results.
# Note: Didnt fully understand this had to use examples from the internet to implement it. 
class SimCache:
    # LRU cache for storing recent equity simulation results to speed up repeated lookups on similar board textures.    
    def __init__(self, maxsize=512):
        self.store = {}
        self._maxsize = maxsize
    # Key is (sorted hero hand, community cards) to ensure order-independence of hole cards and board.
    def key(self, hero_hand, community):
        return (tuple(sorted(hero_hand)), tuple(community))
    # Get cached equity for a given hero hand and community cards, or None if not found.
    def get(self, hero_hand, community):
        return self.store.get(self.key(hero_hand, community))
    # Store equity in cache for a given hero hand and community cards, evicting oldest entry if cache is full.
    def put(self, hero_hand, community, value):
        if len(self.store) >= self._maxsize:
            # Evict a random entry
            self.store.pop(next(iter(self.store)))
        self.store[self._key(hero_hand, community)] = value
# Global cache instance for equity simulations (shared across all bot instances in the process).
equity_cache = SimCache(maxsize=1024)

# Convert hole cards to a key for pre-flop hand strength lookup
def hand_key(hole_cards):
    if len(hole_cards) != 2:
        return ''
    r1, r2 = hole_cards[0][:-1], hole_cards[1][:-1] 
    s1, s2 = hole_cards[0][-1], hole_cards[1][-1]
    suited = 's' if s1 == s2 else 'o'
    v1, v2 = constants.RANK_VALUES.get(r1, 0), constants.RANK_VALUES.get(r2, 0)
    if v1 < v2:
        r1, r2 = r2, r1 
    if r1 == r2:
        return r1 + r2         
    return r1 + r2 + suited     
 
# Pre-flop hand strength tiers based on common poker hand rankings. Tier 1 is strongest, tier 6 is weakest.
def preflop_tier(hole_cards):
    key = hand_key(hole_cards)
    return constants.PREFLOP_TIER.get(key, 6)

# Analyze the community cards to determine board texture and potential dangers for our hand. This helps inform post-flop decisions.
def analyze_board(community_cards):
    #Return a dict describing danger levels on the board.
    #Keys: flush_draw, flush_complete, straight_draw, straight_complete,
    #      paired_board, trips_on_board, monotone
    #All values 0..1 floats (danger score) or bool.

    if not community_cards:
        return dict(flush_draw=0, flush_complete=0, straight_draw=0,
                    straight_complete=0, paired_board=False,
                    trips_on_board=False, monotone=False, danger=0.0)
 
    # Analyze suits and ranks on the board
    suits = [c[-1] for c in community_cards]
    ranks = [c[:-1] for c in community_cards]
    values = sorted(set(constants.RANK_VALUES.get(r, 0) for r in ranks), reverse=True)
    suit_counts = Counter(suits)
    rank_counts = Counter(ranks)
    # Monotone board if all community cards are the same suit (dangerous for flush draws).
    max_suit = max(suit_counts.values())
    monotone = len(community_cards) >= 3 and max_suit == len(community_cards)
 
    flush_draw = 0.0
    flush_complete = 0.0
    if max_suit >= 5:
        flush_complete = 1.0
    elif max_suit == 4:
        flush_draw = 0.85
    elif max_suit == 3 and len(community_cards) == 3:
        flush_draw = 0.45
 
    # Straight detection: find longest run of consecutive ranks, accounting for Ace-low straight.
    def straight_span(vals):
        best = 1
        run = 1
        sv = sorted(set(vals))
        for i in range(1, len(sv)):
            if sv[i] == sv[i-1] + 1:
                run += 1
                best = max(best, run)
            else:
                run = 1
        if 14 in sv:
            low = [v for v in sv if v <= 5]
            best = max(best, len(low) + 1)
        return best
 
    span = straight_span(values)
    straight_complete = 0.0 
    straight_draw = 0.0
    if span >= 5:
        straight_complete = 1.0
    elif span == 4:
        straight_draw = 0.8
    elif span == 3 and len(community_cards) >= 3:
        straight_draw = 0.35
 
    paired_board = any(v >= 2 for v in rank_counts.values())
    trips_on_board = any(v >= 3 for v in rank_counts.values())
 
    # Combine factors into an overall "danger" score for the board, which influences bluffing 
    # and value betting decisions. Weighted more heavily 
    # towards flush/straight draws and completed hands.
    danger = max(flush_draw, flush_complete) * 0.5 + \
             max(straight_draw, straight_complete) * 0.4 + \
             (0.15 if paired_board else 0) + \
             (0.25 if trips_on_board else 0)
    danger = min(danger, 1.0)
    
    return dict(flush_draw=flush_draw, flush_complete=flush_complete,
                straight_draw=straight_draw, straight_complete=straight_complete,
                paired_board=paired_board, trips_on_board=trips_on_board,
                monotone=monotone, danger=danger) 
# Build a weighted deck of possible opponent hole cards based on their VPIP% and PFR%, excluding known cards. Higher VPIP% means a wider range, while lower VPIP% means a tighter range focused on premium hands.
def build_range_deck(deck, vpip_pct, pfr_pct, excluded_cards=None):
    excluded = set(excluded_cards) if excluded_cards else set()
    if vpip_pct is None:
        result = [c for c in deck if c not in excluded]
        random.shuffle(result)
        return result

    tightness = max(0.0, min(1.0, 1.0 - vpip_pct / 100.0))
    high_ranks = {'A', 'K', 'Q', 'J', '10'}
    weighted = []
    for card in deck: 
        if card in excluded:
            continue
        rank = card[:-1]
        weight = 1.0 + tightness * 1.5 if rank in high_ranks else 1.0
        count = max(1, round(weight * 10))
        weighted.extend([card] * count)
    random.shuffle(weighted)
    return weighted
# Get opponent stats from game state, returning VPIP%, PFR%, aggression factor, fold tendency, WTSD% and hands played. Uses defaults to avoid division by zero.
def get_opponent_stats(game_state, player):
    session = game_state["stats"].session
    s = session.get(player, {})
    hands = s.get("hands_played") or 1
    calls = s.get("calls") or 1
    total_actions = s.get("folds", 0) + calls + s.get("bets", 0) + s.get("raises", 0)

    return {
        "vpip_pct":  s.get("vpip", 0) / hands * 100,
        "pfr_pct":   s.get("pfr", 0)  / hands * 100,
        "agg":       (s.get("bets", 0) + s.get("raises", 0)) / calls,
        "fold_tend": s.get("folds", 0) / max(total_actions, 1),
        "wtsd_pct":  s.get("went_to_showdown", 0) / hands * 100,
        "hands":     hands,
    }


def classify_opponent(game_state, player):
    s = get_opponent_stats(game_state, player)
    if s["hands"] < 5:
        return "unknown"
    tight = s["vpip_pct"] < 30
    agg   = s["agg"] > 1.2
    if tight and agg: return "tight-aggressive"
    if tight:         return "tight-passive"
    if agg:           return "loose-aggressive"
    return "loose-passive"

def estimate_equity(game_state, player, simulations=600, use_cache=True):
    hero_hand = game_state["players"][player]["hand"][:]
    community = game_state["community_cards"][:]
    full_deck = game_state["deck"][:]

    if use_cache and len(community) >= 4:
        cached = equity_cache.get(hero_hand, community)
        if cached is not None:
            return cached

    known_cards = set(hero_hand + community)
    deck = [c for c in full_deck if c not in known_cards]

    opponents = [
        p for p in game_state["players"]
        if p != player and not game_state["players"][p]["folded"]
    ]
    if not opponents:
        return 1.0

    wins = ties = 0
    cards_needed_for_board = 5 - len(community)

    for _ in range(simulations):
        sim_deck = deck[:]
        random.shuffle(sim_deck)

        sim_board = community[:]
        for _ in range(cards_needed_for_board):
            sim_board.append(sim_deck.pop())

        hero_score = rank_hand(hero_hand + sim_board)

        used = set(hero_hand + sim_board)
        best_opp_score = None

        for opp in opponents:
            vpip = get_opponent_stats(game_state, opp)["vpip_pct"]
            range_deck = build_range_deck(sim_deck, vpip, get_opponent_stats(game_state, opp)["pfr_pct"], excluded_cards=used)
            c1, c2 = range_deck.pop(), range_deck.pop()
            used.add(c1)
            used.add(c2)
            opp_score = rank_hand([c1, c2] + sim_board)
            if best_opp_score is None or opp_score > best_opp_score:
                best_opp_score = opp_score

        if hero_score > best_opp_score:
            wins += 1
        elif hero_score == best_opp_score:
            ties += 1

    result = (wins + ties * 0.5) / simulations

    if use_cache and len(community) >= 4:
        equity_cache.put(hero_hand, community, result)

    return result

def preflop_decision(game_state, player, legal_actions):

    #Returns (action, amount) using tier + position + opponent reads.
    #Does NOT call estimate_equity (too slow preflop for many sims).
    players        = game_state["player_order"]
    dealer_idx     = game_state["dealer_index"]
    n              = len(players)
    my_idx         = players.index(player)
 
    # Position: 0=UTG … 1=BTN (normalised)
    pos_score = ((my_idx - dealer_idx) % n) / max(n - 1, 1)
    late_pos  = pos_score >= 0.6
 
    hole    = game_state["players"][player]["hand"]
    tier    = preflop_tier(hole)
    chips   = game_state["players"][player]["chips"]
    pot     = game_state["pot"]
    to_call = max(0, game_state["current_bet"] - game_state["players"][player]["bet"])
    min_raise = game_state["min_raise"]
    bb      = game_state["big_blind"]
 
    # Classify opponents facing us
    active_opps = [p for p in players if p != player
                   and not game_state["players"][p]["folded"]]
    opp_types = [classify_opponent(game_state, opp) for opp in active_opps]
    any_lag = 'loose-aggressive' in opp_types
 
    # Decision logic
    if tier == 1:   # AA, KK, QQ, AKs – always play big
        if "raise" in legal_actions:
            amount = min(max(min_raise, pot + to_call), chips)
            return "raise", amount
        if "bet" in legal_actions:
            amount = min(max(min_raise, bb * 3), chips)
            return "bet", amount
        if "call" in legal_actions:
            return "call", None
 
    elif tier == 2:  # JJ, TT, AQs, AKo …
        if "raise" in legal_actions and random.random() < 0.8:
            amount = min(max(min_raise, bb * 3), chips)
            return "raise", amount
        if "call" in legal_actions:
            return "call", None
 
    elif tier == 3:  # 99-77, ATs, KQs …
        if late_pos and "raise" in legal_actions and random.random() < 0.6:
            amount = min(max(min_raise, bb * 2), chips)
            return "raise", amount
        if "call" in legal_actions and (not any_lag or random.random() < 0.5):
            return "call", None
        if "check" in legal_actions:
            return "check", None
 
    elif tier == 4:  # Suited connectors, medium pairs
        if late_pos and "call" in legal_actions and random.random() < 0.7:
            return "call", None
        if "check" in legal_actions:
            return "check", None
 
    elif tier == 5:  # Speculative
        if late_pos and to_call <= bb and "call" in legal_actions and random.random() < 0.5:
            return "call", None
        if "check" in legal_actions:
            return "check", None
 
    # Tier 6 / default – fold to any bet, check if free
    if to_call > 0:
        return "fold", None
    if "check" in legal_actions:
        return "check", None
    return "fold", None
 
  
def should_bluff(game_state, player, texture, equity):
   
    if equity > 0.55:
        return False, 0   # just value-bet
 
    players  = game_state["player_order"]
    n        = len(players)
    my_idx   = players.index(player)
    dealer   = game_state["dealer_index"]
    pos_score = ((my_idx - dealer) % n) / max(n - 1, 1)
    late_pos  = pos_score >= 0.6
 
    active_opps = [p for p in players if p != player
                   and not game_state["players"][p]["folded"]]
    if len(active_opps) > 2:
        return False, 0    # multi-way bluffs rarely work
 
    # Opponent fold tendency weighted bluff probability
    avg_fold = sum(get_opponent_stats(game_state, opp) for opp in active_opps) / max(len(active_opps), 1)
 
    # Base bluff frequency
    bluff_prob = 0.08
    if late_pos:
        bluff_prob += 0.10
    if texture['danger'] > 0.5:          # scare cards on board
        bluff_prob += 0.12
    if avg_fold > 0.55:                   # opponent folds a lot
        bluff_prob += 0.15
    if texture['flush_complete'] or texture['straight_complete']:
        bluff_prob += 0.08               # representing the nuts
 
    bluff_prob = min(bluff_prob, 0.45)
 
    if random.random() < bluff_prob:
        # Sizing: larger bluff on scarier boards
        sizing = 0.5 + texture['danger'] * 0.4   # 50%–90% of pot
        return True, sizing
    return False, 0

 
def value_size(equity, pot, chips, min_raise):
    #Return a bet/raise amount based on equity strength.
    if equity > 0.85:
        frac = random.uniform(0.7, 1.0)   # big value
    elif equity > 0.70:
        frac = random.uniform(0.5, 0.75)
    elif equity > 0.55:
        frac = random.uniform(0.33, 0.55)
    else:
        frac = random.uniform(0.25, 0.40)
    amount = max(min_raise, int(pot * frac))
    # Add small random noise to be less robotic
    noise = random.randint(-min_raise // 2, min_raise // 2)
    return min(max(min_raise, amount + noise), chips)

# Human strategy: prompts user for action and amount, validating against legal actions. Simple text-based interface.
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
# Random bot strategy: chooses randomly among legal actions, with some logic to avoid illegal bets/raises and to add variability in bet sizing. No hand analysis.
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
# Monte Carlo bot strategy: uses pre-flop tier-based decisions, and post-flop equity estimation with board texture analysis to make informed decisions. Adjusts aggression based on hand strength, pot odds, and opponent tendencies. Also includes a bluffing component that considers board texture and opponent fold tendencies.
def monte_carlo_bot_strategy(game_state, player, legal_actions):
    stage    = game_state["stage"]
    chips    = game_state["players"][player]["chips"]
    pot      = game_state["pot"]
    to_call  = max(0, game_state["current_bet"] - game_state["players"][player]["bet"])
    min_raise = game_state["min_raise"]
 
    #Pre-flop: use fast tier-based strategy
    if stage == "preflop":
        return preflop_decision(game_state, player, legal_actions)
 
    #Post-flop: run Monte Carlo
    sims = {"flop": 400, "turn": 600, "river": 900}.get(stage, 400)
    equity = estimate_equity(game_state, player, simulations=sims)
 
    texture = analyze_board(game_state["community_cards"])
 
    pot_odds = to_call / (pot + to_call) if to_call > 0 else 0.0
 
    # Adjust equity estimate downward on dangerous boards when we don't have the nuts
    danger_discount = texture['danger'] * 0.08
    adj_equity = max(0.0, equity - danger_discount)
 
    #Strong hand: value bet
    if adj_equity > 0.72:
        if "raise" in legal_actions:
            return "raise", value_size(adj_equity, pot, chips, min_raise)
        if "bet" in legal_actions:
            return "bet", value_size(adj_equity, pot, chips, min_raise)
        if "call" in legal_actions:
            return "call", None
 
    #Medium hand: call / small bet
    if adj_equity > 0.55:
        if "raise" in legal_actions and random.random() < 0.35:
            return "raise", value_size(adj_equity, pot, chips, min_raise)
        if "call" in legal_actions:
            return "call", None
        if "check" in legal_actions:
            return "check", None
 
    #Marginal hand: pot-odds decision
    if adj_equity > pot_odds:
        if "call" in legal_actions:
            return "call", None
        if "check" in legal_actions:
            return "check", None
 
    #Consider bluffing
    if to_call == 0:
        do_bluff, bluff_sizing = should_bluff(game_state, player, texture, equity)
        if do_bluff:
            amount = min(max(min_raise, int(pot * bluff_sizing)), chips)
            if "bet" in legal_actions:
                return "bet", amount
 
    # Default: fold to bets, check if free 
    if to_call > 0:
        return "fold", None
    if "check" in legal_actions:
        return "check", None
    return "fold", None

# Easy bot strategy: uses pre-flop tiers for initial decisions, and a simple equity threshold post-flop to decide when to call, bet, or fold. Does not consider board texture or opponent tendencies, making it more predictable and easier to exploit.
def easy_bot_strategy(game_state, player, legal_actions):
    stage   = game_state["stage"]
    to_call = max(0, game_state["current_bet"] - game_state["players"][player]["bet"])
 
    if stage == "preflop":
        tier = preflop_tier(game_state["players"][player]["hand"])
        if tier <= 2:
            if "raise" in legal_actions:
                return "raise", game_state["min_raise"]
            if "call" in legal_actions:
                return "call", None
        elif tier <= 4 and to_call == 0:
            return ("check", None)
        if to_call == 0:
            return "check", None
        return "fold", None
 
    equity = estimate_equity(game_state, player, simulations=80, use_cache=True)
 
    if to_call > 0:
        if equity > 0.75 and "call" in legal_actions:
            return "call", None
        if equity > 0.60 and "raise" in legal_actions:
            chips = game_state["players"][player]["chips"]
            return "raise", min(game_state["min_raise"], chips)
        return "fold", None
    else:
        if equity > 0.70 and "bet" in legal_actions:
            chips = game_state["players"][player]["chips"]
            return "bet", min(game_state["min_raise"], chips)
        if "check" in legal_actions:
            return "check", None
    return "fold", None
 
 # Medium bot strategy: combines pre-flop tier-based decisions with post-flop equity estimation and board texture analysis. Adjusts aggression based on hand strength, pot odds, and opponent tendencies. Also includes a bluffing component that considers board texture and opponent fold tendencies, but with more conservative frequencies than the Monte Carlo bot.
def medium_bot_strategy(game_state, player, legal_actions):
    stage     = game_state["stage"]
    chips     = game_state["players"][player]["chips"]
    pot       = game_state["pot"]
    to_call   = max(0, game_state["current_bet"] - game_state["players"][player]["bet"])
    min_raise = game_state["min_raise"]
 
    if stage == "preflop":
        return preflop_decision(game_state, player, legal_actions)
 
    equity = estimate_equity(game_state, player, simulations=250, use_cache=True)
    texture = analyze_board(game_state["community_cards"])
 
    pot_odds = to_call / (pot + to_call) if to_call > 0 else 0.0
    adj_equity = max(0.0, equity - texture['danger'] * 0.05)
 
    # Strong hand
    if adj_equity > 0.70:
        if "raise" in legal_actions:
            return "raise", min(max(min_raise, pot // 3), chips)
        if "call" in legal_actions:
            return "call", None
 
    # Decent hand
    if adj_equity > pot_odds:
        if "call" in legal_actions:
            return "call", None
        if "check" in legal_actions:
            return "check", None
 
    # Light bluff with board awareness
    if to_call == 0 and adj_equity > 0.35 and texture['danger'] > 0.4:
        if random.random() < 0.18 and "bet" in legal_actions:
            return "bet", min(min_raise, chips)
 
    if to_call > 0:
        return "fold", None
    if "check" in legal_actions:
        return "check", None
    return "fold", None
 