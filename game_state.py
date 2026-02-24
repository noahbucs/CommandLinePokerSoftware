# Creates a default state for a poker game
def create_game_state(num_players, starting_chips, small_blind):
    return {
        # Initialize player data
        "players": {
            f"Player {i+1}": {
                "hand": [], 
                "chips": starting_chips,
                "bet": 0,
                "folded": False,
                "all_in": False,
                "strategy": None
            } for i in range(num_players)
        },
        # Initialize game data
        "community_cards": [],
        "pot": 0,
        "deck": [],
        "current_bet": 0,
        "stage": "preflop",
        "last_raiser": None,
        "dealer_index": 0,    
        "player_order": [f"Player {i+1}" for i in range(num_players)],
        "small_blind": small_blind,
        "big_blind": small_blind * 2,
        "min_raise": small_blind * 2,
        "verbose": True,
    }
