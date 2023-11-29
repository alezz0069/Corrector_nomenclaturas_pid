import pandas as pd
from fuzzywuzzy import fuzz
import re

# Function to create the four dataframes
def create_tag_dataframes(df, patterns_templates):
    # Function to convert text to template format
    def convert_to_template_advanced(text, template):
        converted_template = ''
        digit_placeholder = '#'
        letter_placeholder = 'X'
        digit_count = template.count(digit_placeholder)
        letter_count = template.count(letter_placeholder)
        
        for char in text:
            if char.isdigit() and digit_count > 0:
                converted_template += digit_placeholder
                digit_count -= 1
            elif char.isalpha() and letter_count > 0:
                converted_template += letter_placeholder
                letter_count -= 1
            else:
                converted_template += char

        return converted_template

    # Function to calculate fuzzy score only if both exact matches are False
    def calculate_fuzzy_score_advanced(row, pattern_key):
        if not row['tuberia_score_100'] and not row['tag_score_100']:
            pattern = patterns_templates[pattern_key]
            text_template = convert_to_template_advanced(row['text_review'], pattern['template'])
            return fuzz.token_sort_ratio(text_template, pattern['template'])
        return 0

    # Calculate perfect match scores
    df['tuberia_score_100'] = df['text_review'].apply(lambda x: re.fullmatch(patterns_templates['TUBERIA_PATTERN']['regex_pattern'], x) is not None)
    df['tag_score_100'] = df['text_review'].apply(lambda x: re.fullmatch(patterns_templates['TAG_PATTERN']['regex_pattern'], x) is not None)

    # Apply the advanced fuzzy score calculation
    df['tuberia_score_fuzzy'] = df.apply(lambda row: calculate_fuzzy_score_advanced(row, 'TUBERIA_PATTERN'), axis=1)
    df['tag_score_fuzzy'] = df.apply(lambda row: calculate_fuzzy_score_advanced(row, 'TAG_PATTERN'), axis=1)

    # Filtering and creating the specified DataFrames
    TAGS_TUBERIAS_CORRECT = df[df['tuberia_score_100']]
    TAGS_EQUIPOS_CORRECT = df[df['tag_score_100']]
    TAGS_TUBERIAS_CLOSE = df[(df['tuberia_score_fuzzy'] > 20) & (df['tuberia_score_fuzzy'] > df['tag_score_fuzzy'])]
    TAGS_EQUIPOS_CLOSE = df[(df['tag_score_fuzzy'] > 20) & (df['tag_score_fuzzy'] > df['tuberia_score_fuzzy'])]

    return TAGS_TUBERIAS_CORRECT, TAGS_EQUIPOS_CORRECT, TAGS_TUBERIAS_CLOSE, TAGS_EQUIPOS_CLOSE
