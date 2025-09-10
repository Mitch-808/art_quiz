import random
from typing import List, Type, Tuple, Optional, Union
from questions import (
    QuizQuestion,
    YearExactCheck,
    ArtistAuthorshipCheck,
    OldestArtworkCheck,
    FaceOrBodyPresenceCheck,
)
import pandas as pd

STARTING_LIVES = 3
LIVES_BONUS_THRESHOLD = 10
MAX_CONSECUTIVE_PASSES = 3

QUESTION_CLASSES: List[Type[QuizQuestion]] = [
    YearExactCheck,
    ArtistAuthorshipCheck,
    OldestArtworkCheck,
    FaceOrBodyPresenceCheck,
]

class ArtQuizGame:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.lives = STARTING_LIVES
        self.score = 0
        self.consecutive_correct = 0
        self.round_number = 1
        self.consecutive_passes = 0

    def play_round(self) -> Tuple[bool, int, Optional[Union[dict, Tuple[dict, dict]]], Optional[bool]]:
        for _ in range(20):
            question_class = random.choice(QUESTION_CLASSES)
            question = question_class(self.data)
            if question.prepare_question():
                break
        else:
            print("No valid questions are available. Ending game.")
            return False, 0, None, None

        question.show_question()

        while True:
            user_input = input("Answer the question (yes/no or 1/2/s), 'p' to pass, 'q' to quit: ").strip().lower()

            if user_input == 'p':
                if self.consecutive_passes >= MAX_CONSECUTIVE_PASSES:
                    print(f"You reached the max consecutive passes ({MAX_CONSECUTIVE_PASSES}). You must answer or quit.")
                    continue
                print("Question passed without penalty.")
                self.consecutive_passes += 1
                return True, 0, None, None

            if user_input == 'q':
                print("Quitting game.")
                self.lives = 0
                return False, 0, None, None

            result = question.ask_with_preset_answer(user_input)
            if result is None:
                print("Invalid input. Please try again.")
                continue

            is_correct, points, artwork = result
            self.consecutive_passes = 0
            return True, points if is_correct else 0, artwork, is_correct

    def start(self):
        print("Welcome to the Infinite Art Quiz Game!")
        player_name = input("Please enter your name: ").strip() or "Player"

        print(f"\nHello, {player_name}! You start with {self.lives} lives.")
        print(f"Every {LIVES_BONUS_THRESHOLD} consecutive correct answers you gain an extra life.")
        print(f"You may pass up to {MAX_CONSECUTIVE_PASSES} questions in a row without penalty.\n")

        while self.lives > 0:
            keep_playing, points, artwork, correct = self.play_round()

            if not keep_playing or self.lives <= 0:
                break

            if artwork is None:
                # Passed question, no penalty or score change
                continue

            if correct:
                self.score += points
                self.consecutive_correct += 1
                if self.consecutive_correct % LIVES_BONUS_THRESHOLD == 0:
                    self.lives += 1
                    print(f"Congrats! You earned an extra life for {LIVES_BONUS_THRESHOLD} consecutive correct answers!")
            else:
                self.lives -= 1
                self.consecutive_correct = 0

            self.round_number += 1

            # Show URLs after answer — single or multiple artworks
            if isinstance(artwork, (tuple, list)):
                print("\nCheck out the artworks and related info here, if you are curious!")
                for idx, art in enumerate(artwork, start=1):
                    print(f"\nArtwork {idx}: '{art.get('Title', 'N/A')}' by {art.get('Artist', 'N/A')}")
                    print(f"  Image URL: {art.get('Image URL', 'N/A')}")
                    print(f"  Painting Info: {art.get('Painting Info URL', 'N/A')}")
                    print(f"  Artist Info: {art.get('Artist Info URL', 'N/A')}")
            else:
                print("\nCheck out the artwork and related info here, if you are curious!")
                print(f"Image URL: {artwork.get('Image URL', 'N/A')}")
                print(f"Painting Info: {artwork.get('Painting Info URL', 'N/A')}")
                print(f"Artist Info: {artwork.get('Artist Info URL', 'N/A')}")

            # Prompt to continue or quit (only Enter or q)
            while True:
                next_action = input("\nPress Enter for next question or type 'q' to quit: ").strip().lower()
                if next_action == '':
                    break
                elif next_action == 'q':
                    print("Quitting game.")
                    self.lives = 0
                    break
                else:
                    print("Invalid input, please press Enter or 'q'.")

        print(f"\nGame over, {player_name}! Your final score was: {self.score}")

        restart = input("Do you want to play again? [yes/no]: ").strip().lower()
        if restart in {"y", "yes", "ja", "si"}:
            self.__init__(self.data)
            self.start()
        else:
            print("Thanks for playing! Goodbye.")
