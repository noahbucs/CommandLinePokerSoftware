def create_game_state(num_players, starting_chips, small_blind):
    return {
        "players": {
            f"Player {i+1}": {
                "hand": [],
                "chips": starting_chips,
                "bet": 0,
                "folded": False
            } for i in range(num_players)
        },
        "community_cards": [],
        "pot": 0,
        "deck": [],
        "current_bet": 0,
        "stage": "preflop",
        "small_blind": small_blind,
        "big_blind": small_blind * 2
    }
