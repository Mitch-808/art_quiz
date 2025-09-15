from abc import ABC, abstractmethod
from typing import Tuple, Optional, Union
import random
import pandas as pd

# Define sets of accepted yes/no responses for users in various languages and forms
YES_ANSWERS = {"y", "yes", "ja", "si", "true", "t"}
NO_ANSWERS = {"n", "no", "nein", "nah", "false", "f"}

class QuizQuestion(ABC):
    """
    Abstract base class for quiz questions.
    Defines the required methods to create, display, and check questions.
    """
    def __init__(self, data: pd.DataFrame):
        self.data = data

    @abstractmethod
    def prepare_question(self) -> bool:
        """
        Prepare question data for this instance. Return False if not possible.
        """
        pass

    @abstractmethod
    def show_question(self):
        """
        Display the question to the user.
        """
        pass

    @abstractmethod
    def ask_with_preset_answer(self, user_answer: str) -> Optional[Tuple[bool, int, Union[dict, Tuple[dict, dict]]]]:
        """
        Check the user's preset answer, return correctness and scoring info.
        Return None if input is invalid.
        """
        pass

class YearExactCheck(QuizQuestion):
    """
    Question: Is this artwork from this year?
    """
    def prepare_question(self) -> bool:
        pool = self.data.dropna(subset=["Year_exact", "Title", "Artist", "Image URL", "Painting Info URL", "Artist Info URL"])
        if pool.empty:
            return False
        self.artwork = pool.sample(1).iloc[0]
        self.year = int(self.artwork["Year_exact"])
        if random.random() < 0.6:
            self.proposed_year = self.year
            self.correct_answer = True
        else:
            # Other random year from the dataset
            years = [y for y in pool["Year_exact"].dropna().unique() if y != self.year]
            self.proposed_year = int(random.choice(years)) if years else self.year
            self.correct_answer = (self.proposed_year == self.year)
        return True

    def show_question(self):
        print("\n— Year Exact Check —")
        print(f"Is the artwork titled '{self.artwork['Title']}' by '{self.artwork['Artist']}' from the year {self.proposed_year}?")

    def ask_with_preset_answer(self, user_answer: str) -> Optional[Tuple[bool, int, dict]]:
        if user_answer in YES_ANSWERS:
            is_yes = True
        elif user_answer in NO_ANSWERS:
            is_yes = False
        else:
            return None
        is_correct = (is_yes == self.correct_answer)
        print("Correct!" if is_correct else f"Wrong. The actual year is {self.year}.")
        return is_correct, int(is_correct), self.artwork.to_dict()

class ArtistAuthorshipCheck(QuizQuestion):
    """
    Question: Did this artist make this artwork?
    """
    def prepare_question(self) -> bool:
        pool = self.data.dropna(subset=["Artist", "Title", "Image URL", "Painting Info URL", "Artist Info URL"])
        if pool.empty:
            return False
        self.artwork = pool.sample(1).iloc[0]
        self.actual_artist = self.artwork["Artist"]
        # 50%: propose actual artist, 50%: propose a random other artist
        if random.random() < 0.5:
            self.proposed_artist = self.actual_artist
            self.correct_answer = True
        else:
            other_artists = pool.loc[pool["Artist"].str.lower() != self.actual_artist.lower(), "Artist"].unique()
            self.proposed_artist = random.choice(other_artists) if len(other_artists) > 0 else self.actual_artist
            self.correct_answer = (self.proposed_artist == self.actual_artist)
        return True

    def show_question(self):
        print("\n— Artist Authorship —")
        print(f"Did the artist '{self.proposed_artist}' create the artwork titled '{self.artwork['Title']}'?")

    def ask_with_preset_answer(self, user_answer: str) -> Optional[Tuple[bool, int, dict]]:
        if user_answer in YES_ANSWERS:
            is_yes = True
        elif user_answer in NO_ANSWERS:
            is_yes = False
        else:
            return None
        is_correct = (is_yes == self.correct_answer)
        print("Correct!" if is_correct else f"Wrong. The actual artist is {self.actual_artist}.")
        return is_correct, int(is_correct), self.artwork.to_dict()

class OldestArtworkCheck(QuizQuestion):
    """
    Question: Which of these two artworks is older?
    """
    def prepare_question(self) -> bool:
        pool = self.data.dropna(subset=["Year_exact", "Title", "Artist", "Image URL", "Painting Info URL", "Artist Info URL"])
        if len(pool) < 2:
            return False
        sample_two = pool.sample(2)
        self.art1 = sample_two.iloc[0]
        self.art2 = sample_two.iloc[1]
        return True

    def show_question(self):
        print("\n— Age Comparison —")
        print(f"1) '{self.art1['Title']}' by {self.art1['Artist']}")
        print(f"2) '{self.art2['Title']}' by {self.art2['Artist']}")
        print("Which artwork is older or are they the same age?")
        print("Options: 1 (first older), 2 (second older), s (same age)")

    def ask_with_preset_answer(self, user_answer: str) -> Optional[Tuple[bool, int, Tuple[dict, dict]]]:
        if user_answer not in {"1", "2", "s"}:
            return None
        year1 = int(self.art1["Year_exact"])
        year2 = int(self.art2["Year_exact"])
        if year1 == year2:
            correct_answer = "s"
        elif year1 < year2:
            correct_answer = "1"
        else:
            correct_answer = "2"
        is_correct = (user_answer == correct_answer)
        print(f"Correct! Years were 1: {year1}, 2: {year2}" if is_correct else f"Wrong. Years were 1: {year1}, 2: {year2}")
        return is_correct, int(is_correct), (self.art1.to_dict(), self.art2.to_dict())

class FaceOrBodyPresenceCheck(QuizQuestion):
    """
    Question: Does this artwork depict a human face or body?
    """
    def prepare_question(self) -> bool:
        pool = self.data.dropna(subset=["Face_or_body", "Title", "Image URL", "Painting Info URL", "Artist Info URL"])
        if pool.empty:
            return False
        self.artwork = pool.sample(1).iloc[0]
        presence_info = self.artwork["Face_or_body"].lower()
        self.correct_answer = presence_info in {"face", "body"}
        return True

    def show_question(self):
        print("\n— Face or Body Presence —")
        print(f"Does the artwork '{self.artwork['Title']}' depict a human face or body?")

    def ask_with_preset_answer(self, user_answer: str) -> Optional[Tuple[bool, int, dict]]:
        if user_answer in YES_ANSWERS:
            is_yes = True
        elif user_answer in NO_ANSWERS:
            is_yes = False
        else:
            return None
        is_correct = (is_yes == self.correct_answer)
        print("Correct!" if is_correct else f"Wrong. The presence is: {self.artwork['Face_or_body'].lower()}")
        return is_correct, int(is_correct), self.artwork.to_dict()
