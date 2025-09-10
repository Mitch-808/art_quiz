from pathlib import Path
from data_loader import load_artwork_data
from game import ArtQuizGame


def main():
    quiz_path = Path(r"C:\Users\Student\Desktop\PROGRAMMING\art_quiz\clean_quiz_core_metadata.tsv")
    urls_path = Path(r"C:\Users\Student\Desktop\PROGRAMMING\art_quiz\WikiArt-info.tsv")

    if not quiz_path.exists() or not urls_path.exists():
        print(f"Quiz file or URLs file not found.")
        return

    data = load_artwork_data(quiz_path, urls_path)
    game = ArtQuizGame(data)
    game.start()


if __name__ == "__main__":
    main()
