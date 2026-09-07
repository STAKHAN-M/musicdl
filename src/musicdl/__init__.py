from musicdl.menu import main_menu


def main() -> None:
    try:
        main_menu()
    except KeyboardInterrupt:
        print()
