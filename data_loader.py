from pathlib import Path
import pandas as pd
from data_matcher import merge_quiz_and_urls


def load_artwork_data(quiz_path: Path, urls_path: Path) -> pd.DataFrame:
    """
    Loads quiz data and URLs, merges them, and returns enriched dataframe for game.
    """

    print(f"Loading quiz data from: {quiz_path}")
    print(f"Loading artwork URLs from: {urls_path}")

    df = merge_quiz_and_urls(str(quiz_path), str(urls_path))

    # Trim string fields
    for col in ["Artist", "Title", "Style", "Category", "Face_or_body"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df
