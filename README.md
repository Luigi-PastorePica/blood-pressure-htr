# Handwritten Blood Pressure & Heart Rate Log Reader

A Python application that uses OCR (Optical Character Recognition) to extract blood pressure and heart rate data from handwritten medical logs and exports the results to CSV format.

**This is a project I built using Kiro and Claude Sonnet 4. My intention is to test the new agentic IDE and LLM model, trying to see how far I can go with minimal manual source code changes. At this point, the application is able to instantiate a simple user interface (pretty cool, considering I have 0 experience with Tkinter), browse, and upload a document. Handwritten Text Recognition does not work at this time, or at least not with the files I tried uploading.**

## Features

- **Image Processing**: Preprocesses images for optimal OCR results
- **Handwriting Recognition**: Uses Tesseract OCR to extract text from handwritten logs
- **Data Parsing**: Intelligently parses medical data including:
  - Blood pressure readings (systolic/diastolic)
  - Heart rate measurements
  - Dates
- **User-friendly GUI**: Simple Tkinter interface for easy operation
- **CSV Export**: Exports extracted data to CSV format for further analysis

## Requirements

- Python 3.7+
- Tesseract OCR engine

## Installation

**This has only been tested in MacOS thus far. Install on other operating systems at your own risk.**

1. [Optional] While in the project directory, run the following commands to create a venv and activate it.
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```


2. **Install Tesseract OCR**:
   - **macOS**: `brew install tesseract`
   - **Ubuntu/Debian**: `sudo apt install tesseract-ocr`
   - **Windows**: Download from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the application**:
   ```bash
   python main.py
   ```

2. **Load an image**:
   - Click "Browse" to select an image file containing handwritten medical logs
   - Supported formats: PNG, JPG, JPEG, BMP, TIFF, GIF

3. **Process the image**:
   - Click "Process Image" to extract and parse the data
   - The application will display extracted entries in the results table

4. **Export data**:
   - Click "Export to CSV" to save the extracted data
   - Choose a location and filename for your CSV file

## Supported Data Formats

The application can recognize various handwritten formats:

- **Blood Pressure**: 120/80, 120-80
- **Heart Rate**: Standalone numbers (40-200 range)
- **Dates**: MM/DD/YYYY, DD/MM/YYYY, MM-DD-YYYY

## Tips for Better Results

- Use clear, well-lit images
- Ensure handwriting is legible
- Avoid shadows and glare
- Higher resolution images generally work better
- Dark ink on light background works best

## Output Format

The CSV file contains the following columns:
- `Date`: Date of the measurement
- `Systolic_BP`: Systolic blood pressure
- `Diastolic_BP`: Diastolic blood pressure  
- `Heart_Rate`: Heart rate measurement

## Troubleshooting

- **"Tesseract Not Found"**: Make sure Tesseract is installed and in your system PATH
- **Poor recognition**: Try improving image quality, lighting, or handwriting clarity
- **No data extracted**: Check that the image contains recognizable medical data patterns