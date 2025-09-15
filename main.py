from pathlib import Path
from data_loader import load_artwork_data
from game import ArtQuizGame

def main():
    """
    Main entry point for the art quiz game.
    Loads data, initializes the game, and starts the user interface loop.
    """
    quiz_path = Path("clean_quiz_core_metadata.tsv")
    urls_path = Path("WikiArt-info.tsv")

    if not quiz_path.exists() or not urls_path.exists():
        print(f"Quiz file or URLs file not found: '{quiz_path}' or '{urls_path}'")
        return

    try:
        data = load_artwork_data(quiz_path, urls_path)
    except Exception as exc:
        print(f"Failed to load data: {exc}")
        return

    game = ArtQuizGame(data)
    game.start()

if __name__ == "__main__":
    main()
