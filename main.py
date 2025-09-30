#!/usr/bin/env python3
"""
Handwritten Blood Pressure & Heart Rate Log Reader
A Python application that uses OCR to extract data from handwritten medical logs
and exports the results to CSV format.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import pytesseract
import pandas as pd
import re
from datetime import datetime
import os

class BloodPressureLogReader:
    def __init__(self, root):
        self.root = root
        self.root.title("Blood Pressure & Heart Rate Log Reader")
        self.root.geometry("800x600")
        
        self.image_path = None
        self.processed_image = None
        self.extracted_data = []
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Handwritten Medical Log Reader", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection
        ttk.Label(main_frame, text="Select Image:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.file_label = ttk.Label(main_frame, text="No file selected", foreground="gray")
        self.file_label.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        ttk.Button(main_frame, text="Browse", command=self.browse_file).grid(
            row=1, column=2, padx=(10, 0), pady=5)
        
        # Image preview and results frame
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Image preview
        image_frame = ttk.LabelFrame(content_frame, text="Image Preview", padding="5")
        image_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        self.image_label = ttk.Label(image_frame, text="No image loaded")
        self.image_label.pack(expand=True)
        
        # Results frame
        results_frame = ttk.LabelFrame(content_frame, text="Extracted Data", padding="5")
        results_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Treeview for results
        columns = ("Date", "Systolic", "Diastolic", "Heart Rate")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Process Image", command=self.process_image).pack(
            side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Export to CSV", command=self.export_csv).pack(
            side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear Results", command=self.clear_results).pack(
            side=tk.LEFT)
    
    def browse_file(self):
        file_types = [
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select an image file",
            filetypes=file_types
        )
        
        if filename:
            self.image_path = filename
            self.file_label.config(text=os.path.basename(filename), foreground="black")
            self.load_image_preview()
    
    def load_image_preview(self):
        if not self.image_path:
            return
        
        try:
            # Load and resize image for preview
            image = Image.open(self.image_path)
            
            # Calculate size to fit in preview area (max 300x300)
            max_size = 300
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage for tkinter
            photo = ImageTk.PhotoImage(image)
            
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo  # Keep a reference
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")    
   
    def preprocess_image(self, image_path):
        """Preprocess the image for better OCR results"""
        # Read image
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive threshold to get binary image
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to clean up the image
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def extract_text_from_image(self, image):
        """Extract text using Tesseract OCR"""
        try:
            # Configure Tesseract for better handwriting recognition
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789/:-. ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            
            # Extract text
            text = pytesseract.image_to_string(image, config=custom_config)
            return text
        except Exception as e:
            messagebox.showerror("OCR Error", f"Failed to extract text: {str(e)}")
            return ""
    
    def parse_medical_data(self, text):
        """Parse extracted text to find blood pressure and heart rate data"""
        lines = text.strip().split('\n')
        parsed_data = []
        
        # Patterns for different data formats
        # BP format: 120/80 or 120-80
        bp_pattern = r'(\d{2,3})[/-](\d{2,3})'
        # Heart rate: standalone number (usually 60-200 range)
        hr_pattern = r'\b(\d{2,3})\b'
        # Date patterns: MM/DD/YYYY, DD/MM/YYYY, MM-DD-YYYY, etc.
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
            r'(\d{1,2})[/-](\d{1,2})',
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try to extract data from each line
            entry = {}
            
            # Look for date
            for date_pattern in date_patterns:
                date_match = re.search(date_pattern, line)
                if date_match:
                    try:
                        if len(date_match.groups()) == 3:
                            month, day, year = date_match.groups()
                            if len(year) == 2:
                                year = "20" + year
                            entry['date'] = f"{month}/{day}/{year}"
                        else:
                            month, day = date_match.groups()
                            current_year = datetime.now().year
                            entry['date'] = f"{month}/{day}/{current_year}"
                    except:
                        pass
                    break
            
            # Look for blood pressure
            bp_match = re.search(bp_pattern, line)
            if bp_match:
                systolic, diastolic = bp_match.groups()
                # Validate reasonable BP values
                if 70 <= int(systolic) <= 250 and 40 <= int(diastolic) <= 150:
                    entry['systolic'] = systolic
                    entry['diastolic'] = diastolic
            
            # Look for heart rate (exclude BP values)
            hr_matches = re.findall(hr_pattern, line)
            for hr in hr_matches:
                hr_val = int(hr)
                # Check if it's a reasonable heart rate and not part of BP
                if 40 <= hr_val <= 200:
                    # Make sure it's not part of the BP reading
                    if bp_match:
                        bp_numbers = [int(systolic), int(diastolic)]
                        if hr_val not in bp_numbers:
                            entry['heart_rate'] = hr
                            break
                    else:
                        entry['heart_rate'] = hr
                        break
            
            # Only add entry if we found some medical data
            if 'systolic' in entry or 'heart_rate' in entry:
                # Use current date if no date found
                if 'date' not in entry:
                    entry['date'] = datetime.now().strftime("%m/%d/%Y")
                parsed_data.append(entry)
        
        return parsed_data
    
    def process_image(self):
        """Main processing function"""
        if not self.image_path:
            messagebox.showwarning("Warning", "Please select an image file first.")
            return
        
        try:
            # Show processing message
            self.root.config(cursor="wait")
            self.root.update()
            
            # Preprocess image
            processed_img = self.preprocess_image(self.image_path)
            
            # Extract text
            extracted_text = self.extract_text_from_image(processed_img)
            
            if not extracted_text.strip():
                messagebox.showwarning("Warning", "No text could be extracted from the image.")
                return
            
            # Parse medical data
            self.extracted_data = self.parse_medical_data(extracted_text)
            
            # Update UI with results
            self.update_results_display()
            
            if not self.extracted_data:
                messagebox.showinfo("Info", "No medical data patterns found in the extracted text.")
            else:
                messagebox.showinfo("Success", f"Successfully extracted {len(self.extracted_data)} entries.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Processing failed: {str(e)}")
        
        finally:
            self.root.config(cursor="")
    
    def update_results_display(self):
        """Update the treeview with extracted data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add new items
        for entry in self.extracted_data:
            values = (
                entry.get('date', ''),
                entry.get('systolic', ''),
                entry.get('diastolic', ''),
                entry.get('heart_rate', '')
            )
            self.tree.insert('', 'end', values=values)
    
    def export_csv(self):
        """Export extracted data to CSV file"""
        if not self.extracted_data:
            messagebox.showwarning("Warning", "No data to export. Please process an image first.")
            return
        
        try:
            # Ask user for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save CSV file"
            )
            
            if filename:
                # Create DataFrame
                df_data = []
                for entry in self.extracted_data:
                    df_data.append({
                        'Date': entry.get('date', ''),
                        'Systolic_BP': entry.get('systolic', ''),
                        'Diastolic_BP': entry.get('diastolic', ''),
                        'Heart_Rate': entry.get('heart_rate', '')
                    })
                
                df = pd.DataFrame(df_data)
                df.to_csv(filename, index=False)
                
                messagebox.showinfo("Success", f"Data exported successfully to {filename}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def clear_results(self):
        """Clear all results"""
        self.extracted_data = []
        self.update_results_display()


def main():
    # Check if Tesseract is available
    try:
        pytesseract.get_tesseract_version()
    except Exception:
        messagebox.showerror(
            "Tesseract Not Found", 
            "Tesseract OCR is not installed or not found in PATH.\n"
            "Please install Tesseract OCR to use this application.\n\n"
            "On macOS: brew install tesseract\n"
            "On Ubuntu: sudo apt install tesseract-ocr\n"
            "On Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
        )
        return
    
    root = tk.Tk()
    app = BloodPressureLogReader(root)
    root.mainloop()


if __name__ == "__main__":
    main()