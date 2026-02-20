import game_texts


def show_main_menu():
    while True:
        print("\n" + "=" * 40)
        print(game_texts.MENU_WELCOME)
        print("=" * 40)
        print(game_texts.MENU_OPTIONS)

        choice = input(game_texts.MENU_PROMPT)

        if choice == "1":
            return choose_game_mode()
        elif choice == "2":
            print(game_texts.RULES_TEXT)
        elif choice == "3":
            print("Goodbye!")
            return None
        else:
            print("Invalid selection. Try again.")


def choose_game_mode():
    while True:
        print("\nSelect Game Mode:")
        print(game_texts.GAME_MODE_OPTIONS)

        choice = input("Select mode (1-3): ")

        if choice in ["1", "2", "3"]:
            return choice
        else:
            print("Invalid selection.")