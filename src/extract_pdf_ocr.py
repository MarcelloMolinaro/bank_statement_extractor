import fitz  # PyMuPDF
import pytesseract
from pytesseract import Output
import cv2
import numpy as np
import pandas as pd
import os
import yaml
import csv
import re
from datetime import datetime

# Load configuration
with open(os.path.join(os.path.dirname(__file__), '..', 'config.yml'), 'r') as f:
    config = yaml.safe_load(f)

def extract_year_from_filename(filename):
    """Extract year from filename like '3_29_2024_amalgamated.pdf'."""
    match = re.search(r'(\d{4})', filename)
    return int(match.group(1)) if match else datetime.now().year

def categorize(desc):
    """Categorize transaction based on description."""
    d = desc.upper()
    for keyword in config['categories']:
        if keyword in d:
            return config['categories'][keyword]
    return ""

def process_page_with_ocr(page, page_num, statement_year):
    """Process a single page with OCR and return transactions."""
    # Skip page 2 (legal text/disclaimers)
    if page_num == 2:
        return []
    
    # For page 3, check if it contains transaction data first
    if page_num == 3:
        # Quick OCR check to see if page 3 has transaction headers
        pix = page.get_pixmap(dpi=150)  # Lower DPI for quick check
        img_data = pix.tobytes("ppm")
        img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        quick_text = pytesseract.image_to_string(gray)
        
        # Check for transaction table headers
        if not ("Date" in quick_text and "Activity Description" in quick_text and 
                ("Deposits" in quick_text or "Withdrawal" in quick_text)):
            return []  # Skip this page - no transaction data
    
    # Render PDF page as image
    pix = page.get_pixmap(dpi=300)
    img_data = pix.tobytes("ppm")
    img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # Run OCR with coordinates
    ocr_data = pytesseract.image_to_data(gray, output_type=Output.DICT)

    # Group words by y-coordinate (rows)
    rows = {}
    tolerance = 5
    y_start = 1955 if page_num == 1 else 640
    y_end = 2500 if page_num == 1 else 1050

    for i, word in enumerate(ocr_data['text']):
        if not word.strip():
            continue
        x = ocr_data['left'][i]
        y = ocr_data['top'][i]
        
        if y < y_start or y > y_end:
            continue
            
        row_key = None
        for existing_y in rows:
            if abs(existing_y - y) <= tolerance:
                row_key = existing_y
                break
        if row_key is None:
            row_key = y
            rows[row_key] = []
        rows[row_key].append({'text': word, 'x': x})

    # Assign words to columns
    x_ranges = {
        'Date': (135, 296),
        'Description': (296, 1643),
        'Credit': (1643, 2052),
        'Debit': (2052, 2470)
    }
    
    data = []
    for y in sorted(rows):
        row_data = {'Date':'', 'Description':'', 'Credit':'', 'Debit':''}
        for word_info in rows[y]:
            x = word_info['x']
            text = word_info['text']
            for col, (x_min, x_max) in x_ranges.items():
                if x_min <= x <= x_max:
                    if row_data[col]:
                        row_data[col] += ' ' + text
                    else:
                        row_data[col] = text
                    break
        
        # Skip header rows
        if (row_data['Date'].upper() == 'DATE' and 
            'DESCRIPTION' in row_data['Description'].upper()):
            continue
            
        if any(row_data[col] for col in ['Date', 'Description', 'Credit', 'Debit']):
            data.append(row_data)

    # Handle multi-line descriptions
    if not data:
        return []
    
    processed_data = []
    i = 0
    while i < len(data):
        current_row = data[i].copy()
        
        # Check for continuation lines
        while (i + 1 < len(data) and 
               not data[i + 1]['Date'] and 
               data[i + 1]['Description']):
            current_row['Description'] += ' ' + data[i + 1]['Description']
            i += 1
        
        # Move non-dollar text from Credit/Debit to Description
        if (current_row['Credit'] and not current_row['Credit'].startswith('$') and 
            'DEPOSIT' not in current_row['Credit'].upper() and
            'WITHDRAWAL' not in current_row['Credit'].upper()):
            current_row['Description'] += ' ' + current_row['Credit']
            current_row['Credit'] = ''
        
        if (current_row['Debit'] and not current_row['Debit'].startswith('$') and
            'DEPOSIT' not in current_row['Debit'].upper() and
            'WITHDRAWAL' not in current_row['Debit'].upper()):
            current_row['Description'] += ' ' + current_row['Debit']
            current_row['Debit'] = ''
        
        processed_data.append(current_row)
        i += 1
    
    return processed_data

def process_pdf_with_ocr(single_pdf_path):
    """Process a single PDF file and return transactions."""
    # Extract year from filename
    filename = os.path.basename(single_pdf_path)
    statement_year = extract_year_from_filename(filename)
    
    doc = fitz.open(single_pdf_path)
    file_data = []
    
    for page_num, page in enumerate(doc, start=1):
        page_data = process_page_with_ocr(page, page_num, statement_year)
        
        # Handle cross-page continuations
        if file_data and page_data:
            first_row = page_data[0]
            if (not first_row['Date'] and first_row['Description'] and 
                not first_row['Credit'] and not first_row['Debit']):
                # This is a continuation, append to the last row of file_data
                last_row_idx = len(file_data) - 1
                file_data[last_row_idx]['Description'] += ' ' + first_row['Description']
                page_data = page_data[1:]
        
        file_data.extend(page_data)
    
    doc.close()
    
    # Add year to dates and format for CSV
    csv_data = []
    for row in file_data:
        # Format date with year
        date_str = row['Date']
        if date_str and '/' in date_str:
            try:
                # Parse MM/DD format and add year
                month, day = date_str.split('/')
                dt = datetime(statement_year, int(month), int(day))
                formatted_date = dt.strftime("%m/%d/%Y")
            except:
                formatted_date = date_str
        else:
            formatted_date = date_str
        
        # Categorize transaction
        desc = row['Description']
        category = categorize(desc)
        
        csv_data.append({
            'Date': formatted_date,
            'Category': category,
            'Description': desc,
            'Debit Amount': row['Debit'] if row['Debit'] else "",
            'Credit Amount': row['Credit'] if row['Credit'] else ""
        })
    
    return csv_data

def main():
    """Main processing function."""
    pdf_path = config['paths']['pdf_path']
    master_rows = []
    
    if os.path.isdir(pdf_path):
        for name in sorted(os.listdir(pdf_path)):
            if name.lower().endswith(".pdf"):
                master_rows.extend(process_pdf_with_ocr(os.path.join(pdf_path, name)))
    else:
        master_rows.extend(process_pdf_with_ocr(pdf_path))

    # Sort by date
    if master_rows:
        # Sort transactions by date
        def parse_date_for_sorting(date_str):
            try:
                return datetime.strptime(date_str, "%m/%d/%Y")
            except:
                return datetime.min  # Put invalid dates at the beginning
        
        master_rows.sort(key=lambda x: parse_date_for_sorting(x['Date']))
        
        print("\n" + "="*60)
        print("--- COMBINED DATA FROM ALL FILES ---")
        print("="*60)
        combined_df = pd.DataFrame(master_rows)
        print(combined_df)
        print(f"\nTotal transactions found: {len(combined_df)}")
        
        # Save to CSV files
        output_dir = "data/output"
        csv_headers = config['csv']['ocr_headers']
        write_individual = config['csv']['write_individual_files']
        
        # Save individual CSV if enabled
        if write_individual:
            individual_csv_path = os.path.join(output_dir, f"output_page_ocr.csv")
            with open(individual_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
                writer.writeheader()
                writer.writerows(master_rows)
            print(f"- Individual: {individual_csv_path}")
        
        # Save master CSV
        master_csv_path = os.path.join(output_dir, "output_master_ocr.csv")
        with open(master_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
            writer.writeheader()
            writer.writerows(master_rows)
        
        print(f"\nCSV files saved:")
        if write_individual:
            print(f"- Individual: {individual_csv_path}")
        print(f"- Master: {master_csv_path}")
    else:
        print("No data found across all files")

if __name__ == "__main__":
    main()