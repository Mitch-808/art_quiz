import pandas as pd
import re

def extract_url(md_text: str) -> str:
    """
    Extracts the URL from a markdown-style hyperlink: [text](url).
    If not in markdown format, returns the input as-is.

    Args:
        md_text (str): The markdown text.
    
    Returns:
        str: Extracted URL or original text if extraction not possible.
    """
    if pd.isna(md_text):
        return ''
    match = re.search(r'\((.*?)\)', str(md_text))
    return match.group(1) if match else md_text

def merge_quiz_and_urls(quiz_path: str, urls_path: str) -> pd.DataFrame:
    """
    Loads and merges the quiz TSV and URLs TSV by normalized 'Artist' and 'Title' keys.
    Cleans up URLs, merges info columns, and returns an enriched DataFrame.

    Args:
        quiz_path (str): File path to the quiz TSV.
        urls_path (str): File path to the URLs/info TSV.

    Returns:
        pd.DataFrame: Combined DataFrame suitable for the quiz game.

    Raises:
        FileNotFoundError: If files cannot be loaded.
        ValueError: If required columns are missing.
    """
    try:
        quiz_df = pd.read_csv(quiz_path, sep='\t')
        urls_df = pd.read_csv(urls_path, sep='\t')
    except Exception as e:
        raise FileNotFoundError(f"Error loading TSV files: {e}")

    for df in [quiz_df, urls_df]:
        for col in ['Artist', 'Title']:
            if col not in df.columns:
                raise ValueError(f"Missing column '{col}' in input data.")
        # Normalize keys for matching
        df['Artist_norm'] = df['Artist'].astype(str).str.lower().str.strip()
        df['Title_norm'] = df['Title'].astype(str).str.lower().str.strip()

    # Clean URL fields in urls_df
    for col in ['Image URL', 'Painting Info URL', 'Artist Info URL']:
        if col in urls_df.columns:
            urls_df[col] = urls_df[col].apply(extract_url)

    # Merge on normalized keys
    merged_df = pd.merge(
        quiz_df,
        urls_df[['Artist_norm', 'Title_norm', 'Image URL', 'Painting Info URL', 'Artist Info URL']],
        how='left',
        on=['Artist_norm', 'Title_norm']
    )

    # Clean up helper columns
    merged_df.drop(columns=['Artist_norm', 'Title_norm'], inplace=True, errors='ignore')

    return merged_df
