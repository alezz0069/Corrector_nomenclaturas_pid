import pandas as pd
import re
import difflib

def calculate_refined_similarity_score(text, template):
    # Splitting logic based on the specific template structure
    text_components = text.split('-')
    template_components = template.split('-')
    total_similarity = 0

    if len(text_components) == len(template_components):
        for t_comp, tmpl_comp in zip(text_components, template_components):
            # Using difflib to calculate the similarity for each component
            similarity = difflib.SequenceMatcher(None, t_comp, tmpl_comp).ratio()
            total_similarity += similarity

        # Average the total similarity
        average_similarity = (total_similarity / len(template_components)) * 100
        return average_similarity
    else:
        return 0  # If the number of components doesn't match, return 0

def extract_and_difflib_match(text, compiled_pattern, template, min_threshold=10, max_threshold=99):
    #"""Extract potential matches using regex and apply refined difflib matching."""
    potential_matches = compiled_pattern.findall(text)
    close_matches = []
    for match in potential_matches:
        similarity = calculate_refined_similarity_score(match, template)
        if min_threshold <= similarity < max_threshold:  # Note: < max_threshold for non-exact matches
            close_matches.append(match)
    return close_matches

def categorize_text(df, compiled_tuberia_pattern, tuberia_template, compiled_tag_pattern, tag_template):
    #"""Categorize text into different DataFrames based on regex patterns."""
    tags_tuberias_correct_list = []
    tags_equipos_correct_list = []
    matched_tuberias_list = []
    matched_equipos_list = []

    for index, row in df.iterrows():
        text = row['text_review']
        row_dict = row.to_dict()
        if compiled_tuberia_pattern.fullmatch(text):
            tags_tuberias_correct_list.append(row_dict)
        elif compiled_tag_pattern.fullmatch(text):
            tags_equipos_correct_list.append(row_dict)

        tuberia_close_matches = extract_and_difflib_match(text, compiled_tuberia_pattern, tuberia_template)
        if tuberia_close_matches:
            for match in tuberia_close_matches:
                matched_tuberias_list.append((row_dict, match))

        equipos_close_matches = extract_and_difflib_match(text, compiled_tag_pattern, tag_template)
        if equipos_close_matches:
            for match in equipos_close_matches:
                matched_equipos_list.append((row_dict, match))

    TAGS_TUBERIAS_CORRECT = pd.DataFrame(tags_tuberias_correct_list)
    TAGS_EQUIPOS_CORRECT = pd.DataFrame(tags_equipos_correct_list)
    TAGS_TUBERIAS_CLOSE = pd.DataFrame([item[0] for item in matched_tuberias_list])
    TAGS_EQUIPOS_CLOSE = pd.DataFrame([item[0] for item in matched_equipos_list])

    return TAGS_TUBERIAS_CORRECT, TAGS_EQUIPOS_CORRECT, TAGS_TUBERIAS_CLOSE, TAGS_EQUIPOS_CLOSE
