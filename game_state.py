from stats import StatsManager
import random
# Creates a default state for a poker game
def create_game_state(num_players, starting_chips, small_blind):
    game_state = {
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
        "dealer_index": random.randint(0,num_players-1),    
        "player_order": [f"Player {i+1}" for i in range(num_players)],
        "small_blind": small_blind,
        "big_blind": small_blind * 2,
        "min_raise": small_blind * 2,
        "verbose": True,
    }

    # Initialize stats manager
    game_state["stats"] = StatsManager(
        players=game_state["player_order"]
        )

    return game_state