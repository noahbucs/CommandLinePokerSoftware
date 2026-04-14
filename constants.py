# For creating deck
RANKS = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
SUITS = ['♥', '♦', '♣', '♠']

STAGES = stages = ["preflop", "flop", "turn", "river"]

STARTINGFUNDS = 1000

STARTINGBLIND = 10

# For hand evaluation
RANK_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5,
    '6': 6, '7': 7, '8': 8, '9': 9,
    '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
}

PREFLOP_TIER = {
    'AA':1,'KK':1,'QQ':1,'AKs':1, #Top tier hands
    'JJ':2,'TT':2,'AQs':2,'AKo':2,'AJs':2, #Strong hands
    '99':3,'88':3,'ATs':3,'AQo':3,'KQs':3,'AJo':3, # Good hands
    '77':3,'66':3,'55':3,'A9s':4,'A8s':4,'KJs':4,'KTs':4,
    'QJs':4,'JTs':4,'KQo':4,'T9s':4,'98s':4, # Playable hands
    '44':5,'33':5,'22':5,'A7s':5,'A6s':5,'A5s':5,'A4s':5,'A3s':5,'A2s':5,
    'K9s':5,'Q9s':5,'J9s':5,'T8s':5,'97s':5,'87s':5,'76s':5,'65s':5,
    'KJo':5,'KTo':5,'QJo':5,'JTo':5, # Speculative hands
    # The rest of the hands are tier 6
    }

RANGE_WEIGHTS = {
    1: 1.0,
    2: 0.85,
    3: 0.70,
    4: 0.50,
    5: 0.30,
    6: 0.10,
    }