from abc import ABC, abstractmethod
from typing import Tuple, Optional
import random
import pandas as pd

YES_ANSWERS = {"y", "yes", "ja", "si", "true", "t"}
NO_ANSWERS = {"n", "no", "nein", "nah", "false", "f"}

class QuizQuestion(ABC):
    def __init__(self, data: pd.DataFrame):
        self.data = data

    @abstractmethod
    def prepare_question(self) -> bool:
        """Prepare question data. Return False if none available."""
        pass

    @abstractmethod
    def show_question(self):
        """Print the question prompt."""
        pass

    @abstractmethod
    def ask_with_preset_answer(self, user_answer: str) -> Optional[Tuple[bool, int, dict]]:
        """Check user_answer, return (correct, points, artwork_dict) or None if invalid."""
        pass


class YearExactCheck(QuizQuestion):
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
        if is_correct:
            print("Correct!")
        else:
            print(f"Wrong. The actual year is {self.year}.")
        return is_correct, int(is_correct), self.artwork.to_dict()


class ArtistAuthorshipCheck(QuizQuestion):
    def prepare_question(self) -> bool:
        pool = self.data.dropna(subset=["Artist", "Title", "Image URL", "Painting Info URL", "Artist Info URL"])
        if pool.empty:
            return False
        self.artwork = pool.sample(1).iloc[0]
        self.actual_artist = self.artwork["Artist"]
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
        if is_correct:
            print("Correct!")
            if not self.correct_answer:
                print(f"The actual artist is {self.actual_artist}.")
        else:
            print(f"Wrong. The actual artist is {self.actual_artist}.")
        return is_correct, int(is_correct), self.artwork.to_dict()


class OldestArtworkCheck(QuizQuestion):
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
        if is_correct:
            print(f"Correct! Years were 1: {year1}, 2: {year2}")
        else:
            print(f"Wrong. Years were 1: {year1}, 2: {year2}")

        # Return both artworks as a tuple of dicts for URL display
        return is_correct, int(is_correct), (self.art1.to_dict(), self.art2.to_dict())



class FaceOrBodyPresenceCheck(QuizQuestion):
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
        if is_correct:
            print("Correct!")
        else:
            print(f"Wrong. The presence is: {self.artwork['Face_or_body'].lower()}")
        return is_correct, int(is_correct), self.artwork.to_dict()
