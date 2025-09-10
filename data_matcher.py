import pandas as pd
import re

def extract_url(md_text):
    """Extract URL from markdown link format [text](url)."""
    if pd.isna(md_text):
        return ''
    match = re.search(r'\((.*?)\)', md_text)
    return match.group(1) if match else md_text


def merge_quiz_and_urls(quiz_path: str, urls_path: str) -> pd.DataFrame:
    """
    Load quiz and URL files, normalize 'Artist' and 'Title', extract plain URLs,
    and merge URLs into quiz data for use in quizzes.
    """

    # Load files as TSV
    quiz_df = pd.read_csv(quiz_path, sep='\t')
    urls_df = pd.read_csv(urls_path, sep='\t')

    # Normalize keys for merge
    for df in [quiz_df, urls_df]:
        df['Artist_norm'] = df['Artist'].str.lower().str.strip()
        df['Title_norm'] = df['Title'].str.lower().str.strip()

    # Clean URL fields in urls_df by extracting raw URLs from markdown links
    for col in ['Image URL', 'Painting Info URL', 'Artist Info URL']:
        if col in urls_df.columns:
            urls_df[col] = urls_df[col].apply(extract_url)

    # Merge quiz data with URLs on normalized artist and title
    merged_df = pd.merge(
        quiz_df,
        urls_df[['Artist_norm', 'Title_norm', 'Image URL', 'Painting Info URL', 'Artist Info URL']],
        how='left',
        on=['Artist_norm', 'Title_norm']
    )

    # Clean up helper columns if desired
    merged_df.drop(columns=['Artist_norm', 'Title_norm'], inplace=True)

    return merged_df
