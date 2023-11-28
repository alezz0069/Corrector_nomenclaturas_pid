import fitz  # PyMuPDF
import pandas as pd

def load_page_annotations(doc, page_num, zoom):
    """
    Load annotations from a given page in the document.
    """
    page = doc.load_page(page_num)
    annotations = []
    for annot in page.annots():
        bbox = annot.rect
        scaled_bbox = [coord * zoom for coord in [bbox.x0, bbox.y0, bbox.x1, bbox.y1]]
        annotations.append({
            "page": page_num,
            "type": annot.type[1],
            "content": annot.info["content"],
            "bbox_x1": scaled_bbox[0],
            "bbox_y1": scaled_bbox[1],
            "bbox_x2": scaled_bbox[2],
            "bbox_y2": scaled_bbox[3]
        })
    return annotations

def extract_comments_with_bboxes(pdf_path, zoom=2):
    """
    Extract comments with bounding boxes from the entire document.
    """
    with fitz.open(pdf_path) as doc:
        comments_with_bboxes = [annot for page_num in range(len(doc)) 
                                for annot in load_page_annotations(doc, page_num, zoom)]
    return pd.DataFrame(comments_with_bboxes)

def process_comments_with_bboxes(pdf_path, csv_path, zoom=2):
    """
    Process comments with bounding boxes and save to a CSV file.
    """
    comments_df = extract_comments_with_bboxes(pdf_path, zoom)
    if comments_df.empty:
        print("DataFrame is empty. No annotations extracted. Consider using OCR.")
        return

    comments_df.to_csv(csv_path, index=False)
    print(f"Comments with bounding boxes saved to {csv_path}")
    return comments_df

def extract_layout(pdf_path, csv_path='/content/ocr_results.csv', zoom=2):
    """
    Extract layout information from a PDF and save results to a CSV file.
    """
    return process_comments_with_bboxes(pdf_path, csv_path, zoom)


