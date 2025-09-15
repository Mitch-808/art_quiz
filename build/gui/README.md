# Infinite Art Quiz Game

This is a Python-based interactive quiz game centered on famous artworks and artists. Players answer questions about artwork years, artist authorship, artwork age comparison, and human face or body depiction.

## Features
- Multiple question types that challenge your knowledge of art history.
- Lives and scoring system with bonuses for consecutive correct answers.
- Pass and quit options with limits to game flow.
- Rich metadata with URLs to artwork images, painting info, and artist info for further exploration.
- Command-line and graphical user interface (Tkinter-based) modes.

## Installation
Requires Python 3.7 or higher and the pandas library.

Install pandas via pip:
```
pip install pandas
```

## Usage
### Command-line mode
Run the main script:
```
python main.py
```

### GUI mode
Run `gui.py` to launch the graphical interface:
```
python gui.py
```

## Data Files
The quiz is based on two TSV files:
- `clean_quiz_core_metadata.tsv`: Contains core quiz data. It was cleaned and processed as part of a separate project.
- `WikiArt-info.tsv`: Contains related artworks and artist URLs. It originates from the WikiArt Emotions dataset by Saif M. Mohammad and Svetlana Kiritchenko, available at https://saifmohammad.com/WebPages/wikiartemotions.html.

- Both files must be present in the working directory.

## Project Structure
- `main.py`: Entry point for command-line gameplay.
- `gui.py`: Graphical interface implementation using Tkinter.
- `game.py`: Core game logic including question flow, scoring, and lives.
- `questions.py`: Definitions of quiz question types and logic.
- `data_loader.py`: Loads and merges TSV data files, prepares data for the quiz.
- `data_matcher.py`: Helper functions to clean and merge quiz and URL data.

## How It Works
- The game loads artwork and artist data merging metadata with URLs.
- Players answer random questions about artworks.
- Correct answers increase score and may grant extra lives.
- Incorrect answers and quitting end the game.
- Passing questions allowed up to a limit without penalty.
