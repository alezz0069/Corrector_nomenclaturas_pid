import cv2
import os
import pandas as pd
from PIL import Image
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import tempfile
import matplotlib.pyplot as plt
import torch

def preprocess_tile(tile):
    # Add your preprocessing logic here, if any
    return tile

def slice_image(img, desired_num_tiles):
    img_height, img_width, _ = img.shape

    num_tiles_height = int((desired_num_tiles)**0.5)
    num_tiles_width = int((desired_num_tiles)**0.5)

    slice_height = img_height // num_tiles_height
    slice_width = img_width // num_tiles_width

    min_overlap_height = int(0.35 * slice_height)
    min_overlap_width = int(0.35 * slice_width)

    step_height = slice_height - min_overlap_height
    step_width = slice_width - min_overlap_width

    tiles = []
    coordinates = []

    y1 = 0
    while y1 + slice_height <= img_height:
        x1 = 0
        while x1 + slice_width <= img_width:
            x2 = x1 + slice_width
            y2 = y1 + slice_height

            tile = img[y1:y2, x1:x2]
            tiles.append(tile)
            coordinates.append((x1, y1))

            x1 += step_width
        y1 += step_height

    return tiles, coordinates, slice_height, slice_width

def process_tile(tile, tile_x1, tile_y1, orientation, model, tile_idx, margin=5, overlap_adjustment=0):
    try:
        if overlap_adjustment:
            tile = tile[overlap_adjustment:-overlap_adjustment, overlap_adjustment:-overlap_adjustment]

        preprocessed_tile = preprocess_tile(tile)
        pil_image = Image.fromarray(preprocessed_tile)

        boxes = []

        with tempfile.NamedTemporaryFile(delete=True, suffix='.png') as temp_file:
            pil_image.save(temp_file.name)
            result = model(DocumentFile.from_images(temp_file.name))

            for block in result.pages[0].blocks:
                for word in block.lines[0].words:
                    box = word.geometry
                    x1_tile, y1_tile = box[0]
                    x2_tile, y2_tile = box[1]

                    x1_global = x1_tile * tile.shape[1] + tile_x1 - margin
                    y1_global = y1_tile * tile.shape[0] + tile_y1 - margin
                    x2_global = x2_tile * tile.shape[1] + tile_x1 + margin
                    y2_global = y2_tile * tile.shape[0] + tile_y1 + margin

                    boxes.append((tile_idx, x1_global, y1_global, x2_global, y2_global, word.value, orientation))

            return boxes
    except Exception as e:
        return {"error": e, "tile_idx": tile_idx}

def ocr_process(jpg_path):
    # Check for GPU availability
    if torch.cuda.is_available():
        print("GPU is available: ", torch.cuda.get_device_name(0))
    else:
        print("GPU is not available. Using CPU.")

    # Check if the image path is valid
    if not os.path.exists(jpg_path):
        print(f"Image not found at {jpg_path}")
        return

    img = cv2.imread(jpg_path)
    if img is None:
        print("Failed to read the image.")
        return

    desired_num_tiles = 90
    tiles, tile_coordinates, slice_height, slice_width = slice_image(img, desired_num_tiles)

    model = ocr_predictor(pretrained=True)

    boxes_list = []
    for idx, tile in enumerate(tiles):
        tile_x1, tile_y1 = tile_coordinates[idx]
        result = process_tile(tile, tile_x1, tile_y1, "horizontal", model, idx, margin=5)
        
        if "error" in result:
            print(f"Error processing tile {idx}: {result['error']}")
        else:
            boxes_list.extend(result)

    df = pd.DataFrame(boxes_list, columns=["tile", "x1", "y1", "x2", "y2", "text", "orientation"])
    df.to_csv("/content/ocr_results.csv", index=False)
    

    for _, row in df.iterrows():
        x1, y1, x2, y2 = row["x1"], row["y1"], row["x2"], row["y2"]
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

    cv2.imwrite("/content/ocr_results_horizontal.jpg", img)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.figure(figsize=(45, 45))
    plt.imshow(img_rgb)
    plt.axis('off')
    plt.show()
    return "/content/ocr_results.csv"
