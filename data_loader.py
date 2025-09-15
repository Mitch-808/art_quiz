from pathlib import Path
import pandas as pd
from data_matcher import merge_quiz_and_urls

def load_artwork_data(quiz_path: Path, urls_path: Path) -> pd.DataFrame:
    """
    Loads quiz data and URLs from the provided paths, merges them,
    trims whitespace from important columns, and returns the final DataFrame for the quiz game.

    Args:
        quiz_path (Path): Path to the TSV file with quiz data.
        urls_path (Path): Path to the TSV file with URLs/info data.

    Returns:
        pd.DataFrame: Combined and cleaned quiz dataframe for use in the quiz.
    
    Raises:
        FileNotFoundError: If either file does not exist.
        ValueError: If merging fails or data is malformed.
    """
    print(f"Loading quiz data from: {quiz_path}")
    print(f"Loading artwork URLs from: {urls_path}")

    if not quiz_path.exists():
        raise FileNotFoundError(f"Quiz data file not found: {quiz_path}")
    if not urls_path.exists():
        raise FileNotFoundError(f"URLs data file not found: {urls_path}")
    
    df = merge_quiz_and_urls(str(quiz_path), str(urls_path))
    
    # Trim whitespace in important string columns, if they exist
    for col in ["Artist", "Title", "Style", "Category", "Face_or_body"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df
