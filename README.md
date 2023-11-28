# Corrector_nomenclaturas_pid
Extrae tags de PID y corrige de acuerdo a un patron de tag inferido

## Installation
To set up your environment to run these scripts, clone the repository and install the necessary dependencies.

bash
git clone https://github.com/alezz0069/Corrector_nomenclaturas_pid.git
cd Corrector_nomenclaturas_pid
pip install -r requirements.txt

## Scripts Overview 
main_py.py: Serves as the central script that coordinates the execution flow of the entire project.
extract_text_layout.py: Analyzes document layouts by loading and processing page annotations.
ocr_with_doctr.py: Employs the doctr library for Optical Character Recognition to digitize text from images.
filter_ocr.py: Refines OCR results, improving the quality of the text extracted from images and documents.
obtain_patterns.py: Retrieves patterns from textual data sources using advanced extraction techniques.
dataframe_tags.py: Utilizes regex and fuzzy matching to extract and analyze data within dataframes.



## Usage
To use these scripts, navigate to the project directory and execute the main script as shown below:

python main_py.py
