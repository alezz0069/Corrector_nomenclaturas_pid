# -*- coding: utf-8 -*-
"""main.py

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1CZRT7gUool6dr1O8P6ktRCny0lkfBDDT
"""

#pip install -r requierements.txt

!sudo apt update
!sudo apt install -y tesseract-ocr
!sudo apt install -y libtesseract-dev


import os
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import re
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def main(pdf_path, jpg_path):
    import extract_text_layout
    import ocr_with_doctr
    import obtain_patterns
    import dataframe_tags

    # Extract text layout
    layout_df = extract_text_layout.extract_layout(pdf_path)

    if layout_df is None or layout_df.empty:
        print(f"The text layout extraction failed for {pdf_path}. Proceeding to OCR now....")
        # Perform OCR and generate ocr_results.csv
        ocr_with_doctr.ocr_process(jpg_path)
        import filter_ocr
        # Once OCR is complete, run the filter_ocr subprogram
        ocr_results_path = "/content/ocr_results.csv"
        image_path = jpg_path
        tesseract_config = '--oem 3 --psm 7'
        final_data=filter_ocr.ocr_text(ocr_results_path, image_path, tesseract_config)
        # Load the final filtered OCR data
        filtered_df = pd.read_csv('/content/ocr_data_final_filtered.csv')
    else:
        # If layout extraction is successful, use it for further processing
        filtered_df = filter_ocr.filter_ocr_data(layout_df)

    # Remaining processing
    # After loading the final filtered OCR data
    filtered_df['num_chars'] = filtered_df['text_review'].apply(len)
    most_common_chars = filtered_df['num_chars'].value_counts().head(2).index.tolist()

    patterns, exact_patterns = obtain_patterns.determine_and_display_patterns(filtered_df, most_common_chars)

    # Display the patterns
    print("Regex Patterns and Templates:", patterns)
    print("Exact Patterns:", exact_patterns)

    # Compile regex patterns from the obtained patterns
    compiled_tuberia_pattern = re.compile(patterns['TUBERIA_PATTERN']['regex_pattern'])
    compiled_tag_pattern = re.compile(patterns['TAG_PATTERN']['regex_pattern'])

    candidates = pd.read_csv('/content/ocr_data_final_filtered.csv')
    #####################################################################ultimo filtrado########
    df=candidates
    # Create a dictionary to store the 'remove' values for each index
    remove_values_dict = {}

    # Function to calculate the area of a bounding box
    def calculate_bbox_area(bbox):
        return bbox.area

    # Iterate through each row
    for index, row in df.iterrows():
        current_bbox = box(row['x1'], row['y1'], row['x2'], row['y2'])
        remove = False

        # Check against all other rows
        for other_index, other_row in df.iterrows():
            if index != other_index:  # Avoid self-comparison
                other_bbox = box(other_row['x1'], other_row['y1'], other_row['x2'], other_row['y2'])

                # Check if the bounding boxes overlap
                if current_bbox.intersects(other_bbox):

                    # Compare the areas of the bounding boxes
                    if calculate_bbox_area(current_bbox) < calculate_bbox_area(other_bbox):
                        remove = True
                    else:
                        remove_values_dict[other_index] = True

                    break

        # Store the 'remove' value for the current index
        remove_values_dict[index] = remove

    # Convert the dictionary to a list for DataFrame column
    remove_values = [remove_values_dict.get(index, False) for index in range(len(df))]

    # Add the 'remove' column to the DataFrame
    df['remove'] = remove_values
    # Filter out the rows marked as True in the 'remove' column
    df = df[df['remove'] == False]

    candidates=df
    #####################################################################fin de ultimo filtrado########

    
    # Process and categorize text using the correct function
    TAGS_TUBERIAS_CORRECT, TAGS_EQUIPOS_CORRECT, TAGS_TUBERIAS_CLOSE, TAGS_EQUIPOS_CLOSE = dataframe_tags.create_tag_dataframes(candidates, patterns)
    # Save DataFrames as CSV files and print confirmation
    print("Tag extraction successful!")
    TAGS_TUBERIAS_CORRECT.to_csv('/content/TAGS_TUBERIAS_CORRECT.csv', index=False)
    print("TAGS_TUBERIAS_CORRECT contains the EXACT TAG matches")
    TAGS_EQUIPOS_CORRECT.to_csv('/content/TAGS_EQUIPOS_CORRECT.csv', index=False)
    print("TAGS_EQUIPOS_CORRECT contains the EXACT TAG matches")
    TAGS_TUBERIAS_CLOSE.to_csv('/content/TAGS_TUBERIAS_CLOSE.csv', index=False)
    print("TAGS_TUBERIAS_CLOSE contains POSIBLE TAG matches")
    TAGS_EQUIPOS_CLOSE.to_csv('/content/TAGS_EQUIPOS_CLOSE.csv', index=False)
    print("TAGS_EQUIPOS_CLOSE contains POSIBLE TAG matches")


    ###############################################################################################OPTIONAL: Drawing and showing the corrections
    import cv2
    from PIL import Image, ImageDraw, ImageFont


    # Load the image
    image_path = jpg_path
    image = Image.open(image_path)

    # Create a drawing context on a transparent layer
    transparent_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(transparent_layer)

    # Define colors with transparency (alpha channel)
    green_color = (0, 255, 0, 128)  # Green with 50% transparency
    yellow_color = (255, 255, 0, 128)  # Yellow with 50% transparency
    purple_color = (128, 0, 128, 128)  # Purple with 50% transparency
    red_color = (255, 0, 0, 255)  # Red with full opacity

    # Define a font for text labels
    font = ImageFont.load_default()

    # Function to draw bounding boxes and text labels for a DataFrame
    def draw_bounding_boxes_and_labels(df, box_color, text_color):
        for index, row in df.iterrows():
            x1, y1, x2, y2 = row['x1'], row['y1'], row['x2'], row['y2']
            text = row['text']
            # Draw the filled bounding box with transparency on the transparent layer
            draw.rectangle([x1, y1, x2, y2], outline=None, fill=box_color)
            # Calculate the text size based on text length and font size
            text_size = (len(text) * 10, 10)  # You may need to adjust the size
            # Draw the text label on the transparent layer
            draw.text(((x1 + x2 - text_size[0]) / 2, y2 + 2), text, fill=text_color, font=font)

    # Draw bounding boxes and text labels for TAGS_TUBERIAS_CORRECT
    draw_bounding_boxes_and_labels(TAGS_TUBERIAS_CORRECT, green_color, red_color)

    # Draw bounding boxes and text labels for TAGS_TUBERIAS_POSSIBLE
    draw_bounding_boxes_and_labels(TAGS_TUBERIAS_CLOSE, yellow_color, red_color)

    # Draw bounding boxes and text labels for TAGS_EQUIPOS_CORRECT
    draw_bounding_boxes_and_labels(TAGS_EQUIPOS_CORRECT, purple_color, red_color)

    # Draw bounding boxes and text labels for TAGS_EQUIPOS_POSSIBLE
    draw_bounding_boxes_and_labels(TAGS_EQUIPOS_CLOSE, yellow_color, red_color)

    # Composite the original image with the transparent layer
    image.paste(transparent_layer, (0, 0), transparent_layer)

    # Save or display the resulting image
    image.show()  # To display the image
    image.save('/content/output_image.jpg')  # To save the image
    print("Corrections drawn: output_image.jpg")

    uploaded_image_path = "/content/output_image.jpg"
    # Display the image
    from IPython.display import display, Image
    display(Image(filename=uploaded_image_path))
    #####################################################################################################Fin de OPTIONAL: Drawing and showing the corrections
if __name__ == "__main__":
    folder_path = '/content'
    jpg_path = '/content/filled_image.jpg'
    pdf_files = [file for file in os.listdir(folder_path) if file.endswith('.pdf')]
    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder_path, pdf_file)
        print(f"Processing {pdf_path} with {jpg_path}")
        main(pdf_path, jpg_path)
