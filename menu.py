import game_texts
import stats


def show_main_menu():
    while True:
        print("\n" + "=" * 40)
        print(game_texts.MENU_WELCOME)
        print("=" * 40)
        print(game_texts.MENU_OPTIONS)

        choice = input(game_texts.MENU_PROMPT)

        if choice == "1":
            settings = choose_game_mode()
            return settings

        elif choice == "2":
            stats.view_stats_menu()

        elif choice == "3":
            stats.clear_stats()

        elif choice == "4":
            print(game_texts.RULES_TEXT)

        elif choice == "5":
            return None

        else:
            print(game_texts.INVALID)


def choose_game_mode():
    while True:
        print("\nSelect Game Mode:")
        print(game_texts.GAME_MODE_OPTIONS)

        choice = input("Select mode (1-3): ")

        if choice == "1":
            num_players = choose_player_count()
            return {"mode": "pvp", "players": num_players}

        elif choice == "2":
            num_players = choose_player_count()
            bot_difficulties = []
            for i in range(2, num_players + 1):
                print(f"\nSet difficulty for Player {i} (bot):")
                bot_difficulties.append(choose_bot_difficulty())
            return {"mode": "pvc", "players": num_players, "bot_difficulties": bot_difficulties}

        elif choice == "3":
            num_players = choose_player_count()
            bot_difficulties = []
            for i in range(1, num_players + 1):
                print(f"\nSet difficulty for Player {i} (bot):")
                bot_difficulties.append(choose_bot_difficulty())
            return {"mode": "cvc", "players": num_players, "bot_difficulties": bot_difficulties}

        else:
            print(game_texts.INVALID)


def choose_player_count():
    while True:
        num_players = input(game_texts.PLAYER_PROMPT)
        if num_players.isdigit() and 2 <= int(num_players) <= 8:
            return int(num_players)
        print(game_texts.INVALID)


def choose_bot_difficulty():
    while True:
        print(game_texts.BOT_DIFFICULTY_PROMPT)
        choice = input("Select difficulty (1-4): ")
        if choice == "1":
            return "easy"
        elif choice == "2":
            return "medium"
        elif choice == "3":
            return "hard"
        elif choice == "4":
            return "chaos"
        else:
            print(game_texts.INVALID)

def play_again():
    while True:
        again = input("\nPlay again? (y/n): ").strip().lower()
        if again in ["y", "n"]:
            return again == "y"
        print(game_texts.INVALID)