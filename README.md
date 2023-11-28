# PID Tag Corrector

The PID Tag Corrector is designed to automate the extraction of equipment tags from Process and Instrumentation Diagrams (P&IDs) based on an inference of nomenclatures. 


## Features
-OCR Enhancement: Processes P&ID images to extract text.

-Tag Recognition: Identifies and extracts tag information from complex diagrams.

-Pattern Inference: Analyzes existing tags to infer the correct naming pattern.

-Dataframe Analysis: Employs regular expressions and fuzzy matching for data extraction and analysis.

-Correction Algorithm: Applies inferred patterns to correct and standardize tag names.

## Components
-main_py.py: The entry point script orchestrating the correction process.

-extract_text_layout.py: Parses P&ID layouts to identify text and tag locations.

-ocr_with_doctr.py: Applies doctr OCR library to convert images to text.

-filter_ocr.py: Filters OCR output to enhance text quality.

-obtain_patterns.py: Infers tagging patterns from the processed text.

-dataframe_tags.py: Analyzes and processes data within pandas dataframes.

## Usage
python main_py.py
