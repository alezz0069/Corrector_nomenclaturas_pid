import pandas as pd
import pytesseract
from PIL import Image
import os

# Function to load and preprocess initial OCR data
def load_and_preprocess_data(file_path):
    df = pd.read_csv(file_path)
    df['text'] = df['text'].astype(str)
    df['num_of_characters'] = df['text'].apply(len)
    return df

# Function to filter the data based on specific patterns and character count
def filter_data(df):
    conditions = (df['text'].str.contains('.*-.*-.*') | df['text'].str.contains('"') |
                  df['text'].str.contains("'") | df['text'].str.contains("/")) & (df['num_of_characters'] > 10)
    filtered_df = df[conditions].copy()
    chars_to_replace = ['"', "'", "(", ")", "."]  # Including period (.) in the list of characters to replace
    for char in chars_to_replace:
        if char == '.':
            filtered_df['text'] =filtered_df['text']
            #filtered_df['text'] = filtered_df['text'].str.replace(char, '-', regex=False)  # Replacing period with hyphen
        else:
            filtered_df['text'] = filtered_df['text'].str.replace(char, '', regex=False)
    return filtered_df
    
# Function to apply OCR to a specific bbox in an image with custom configuration
def apply_ocr_to_bbox(image, bbox, config):
    cropped_img = image.crop(bbox)
    text = pytesseract.image_to_string(cropped_img, lang='eng', config=config)
    return text.strip()

# Function to process OCR data on the filtered data
def process_ocr_data(csv_path, image_path, config):
    ocr_data = pd.read_csv(csv_path)
    ocr_data['text_review'] = ''
    with Image.open(image_path) as img:
        for index, row in ocr_data.iterrows():
            bbox = (row['x1'], row['y1'], row['x2'], row['y2'])
            ocr_data.at[index, 'text_review'] = apply_ocr_to_bbox(img, bbox, config)
    # Replace quotation marks and save the updated OCR data
    ocr_data['text_review'] = ocr_data['text_review'].apply(
        lambda text: text.replace('.', '-').replace('“', '"').replace('”', '"').replace('„', '"').replace('«', '"').replace('»', '"').replace(' ', ''))
    ocr_data.to_csv("/content/ocr_data.csv", index=False)
    return ocr_data


# Check if a smaller bbox is at least threshold% contained within a larger bbox
def is_bbox_contained(small_bbox, big_bbox, threshold=0.50):
    x1_small, y1_small, x2_small, y2_small = small_bbox
    x1_big, y1_big, x2_big, y2_big = big_bbox
    dx = min(x2_small, x2_big) - max(x1_small, x1_big)
    dy = min(y2_small, y2_big) - max(y1_small, y1_big)
    if (dx >= 0) and (dy >= 0):
        area_of_overlap = dx * dy
    else:
        area_of_overlap = 0
    area_of_small_bbox = (x2_small - x1_small) * (y2_small - y1_small)
    return area_of_overlap >= threshold * area_of_small_bbox

# Check if two bboxes are similar in terms of their coordinates
def is_bbox_similar(bbox1, bbox2, coordinate_threshold=100):
    return all(abs(b1 - b2) <= coordinate_threshold for b1, b2 in zip(bbox1, bbox2))

# Check if two bboxes are very close in terms of their coordinates
def is_bbox_very_close(bbox1, bbox2, coordinate_threshold=20):
    return all(abs(b1 - b2) <= coordinate_threshold for b1, b2 in zip(bbox1, bbox2))

# Calculate the area of a bounding box
def get_area(bbox):
    x1, y1, x2, y2 = bbox
    return (x2 - x1) * (y2 - y1)

# Main processing function
def ocr_text(ocr_results_path, image_path, tesseract_config):
    df = load_and_preprocess_data(ocr_results_path)
    TAGS_pipes_df = filter_data(df)
    TAGS_pipes_df.to_csv("/content/ocr_results_tags.csv", index=False)
    
    processed_data = process_ocr_data('/content/ocr_results_tags.csv', image_path, tesseract_config)
    if processed_data is not None:
        processed_data['text_review'] = processed_data['text_review'].str.replace('O', '0', regex=False)
        
        # Additional filtering logic
        bboxes_to_keep = []
        for i, row_i in processed_data.iterrows():
            bbox_i = (row_i['x1'], row_i['y1'], row_i['x2'], row_i['y2'])
            text_review_i = row_i['text_review']
            keep_bbox_i = True
            for j, row_j in processed_data.iterrows():
                if i != j:
                    bbox_j = (row_j['x1'], row_j['y1'], row_j['x2'], row_j['y2'])
                    text_review_j = row_j['text_review']
                    if (is_bbox_contained(bbox_i, bbox_j) or is_bbox_similar(bbox_i, bbox_j) or is_bbox_very_close(bbox_i, bbox_j)) and text_review_i == text_review_j:
                        if get_area(bbox_i) < get_area(bbox_j):
                            keep_bbox_i = False
                            break
            if keep_bbox_i:
                bboxes_to_keep.append(row_i)

        final_filtered_data = pd.DataFrame(bboxes_to_keep)
        final_filtered_data.to_csv('/content/ocr_data_final_filtered.csv', index=False)
        return final_filtered_data
    else:
        return None

# Replace this with the actual paths
ocr_results_path = '/content/ocr_results.csv'
image_path = '/content/filled_image.jpg'
tesseract_config = '--oem 3 --psm 7'

# Run the main processing function
final_data = ocr_text(ocr_results_path, image_path, tesseract_config)
if final_data is not None:
    print("OCR data processed and filtered successfully.")
else:
    print("Failed to process OCR data.")
