import pandas as pd
import re
from fuzzywuzzy import fuzz


def extract_and_fuzzy_match(text, pattern, min_threshold=40, max_threshold=99):
    """Extract potential matches using regex and apply fuzzy matching."""
    potential_matches = re.findall(pattern, text)
    for match in potential_matches:
        similarity = fuzz.ratio(match, text)
        if min_threshold <= similarity <= max_threshold:
            return True
    return False

def categorize_text(df, tuberia_pattern, tag_pattern):
    """Categorize text into different DataFrames based on regex patterns."""
    tags_tuberias_correct_list = []
    tags_equipos_correct_list = []
    matched_tuberias_list = []
    matched_equipos_list = []

    for index, row in df.iterrows():
        text = row['text_review']
        row_dict = row.to_dict()
        if tuberia_pattern.fullmatch(text):
            tags_tuberias_correct_list.append(row_dict)
        elif tag_pattern.fullmatch(text):
            tags_equipos_correct_list.append(row_dict)

        if extract_and_fuzzy_match(text, tuberia_pattern):
            matched_tuberias_list.append(row_dict)
        elif extract_and_fuzzy_match(text, tag_pattern):
            matched_equipos_list.append(row_dict)

    TAGS_TUBERIAS_CORRECT = pd.DataFrame.from_records(tags_tuberias_correct_list)
    TAGS_EQUIPOS_CORRECT = pd.DataFrame.from_records(tags_equipos_correct_list)
    TAGS_TUBERIAS_CLOSE = pd.DataFrame.from_records(matched_tuberias_list)
    TAGS_EQUIPOS_CLOSE = pd.DataFrame.from_records(matched_equipos_list)

    return TAGS_TUBERIAS_CORRECT, TAGS_EQUIPOS_CORRECT, TAGS_TUBERIAS_CLOSE, TAGS_EQUIPOS_CLOSE
