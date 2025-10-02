import fitz  # PyMuPDF
import pytesseract
from pytesseract import Output
import cv2
import numpy as np
import pandas as pd
from extract_utils import get_config, categorize, save_csv, sort_transactions_by_date, get_pdf_files, extract_year_from_filename, format_date_with_year

# Removed - now using shared functions from utils

def process_page_with_ocr(page, page_num, statement_year):
    """Process a single page with OCR and return transactions."""
    config = get_config()
    ocr_config = config['ocr']
    
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
    pix = page.get_pixmap(dpi=ocr_config['dpi'])
    img_data = pix.tobytes("ppm")
    img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # Run OCR with coordinates
    ocr_data = pytesseract.image_to_data(gray, output_type=Output.DICT)

    # Group words by y-coordinate (rows)
    rows = {}
    tolerance = ocr_config['row_tolerance']
    y_start = ocr_config['page_1_y_start'] if page_num == 1 else ocr_config['page_3_y_start']
    y_end = ocr_config['page_1_y_end'] if page_num == 1 else ocr_config['page_3_y_end']

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

    # Assign words to columns using config
    x_ranges = {col: tuple(coords) for col, coords in ocr_config['x_ranges'].items()}
    
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
    statement_year = extract_year_from_filename(single_pdf_path)
    
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
    
    # Format for CSV
    csv_data = []
    for row in file_data:
        formatted_date = format_date_with_year(row['Date'], statement_year)
        
        csv_data.append({
            'Date': formatted_date,
            'Category': categorize(row['Description']),
            'Description': row['Description'],
            'Debit Amount': row['Debit'] if row['Debit'] else "",
            'Credit Amount': row['Credit'] if row['Credit'] else ""
        })
    
    return csv_data

def main():
    """Main processing function."""
    config = get_config()
    pdf_files = get_pdf_files(config['paths']['pdf_path'])
    
    master_rows = []
    for pdf_file in pdf_files:
        master_rows.extend(process_pdf_with_ocr(pdf_file))

    if master_rows:
        # Sort transactions by date
        master_rows = sort_transactions_by_date(master_rows)
        
        print("\n" + "="*60)
        print("--- COMBINED DATA FROM ALL FILES ---")
        print("="*60)
        combined_df = pd.DataFrame(master_rows)
        print(combined_df)
        print(f"\nTotal transactions found: {len(combined_df)}")
        
        # Save CSV files
        csv_headers = config['csv']['ocr_headers']
        write_individual = config['csv']['write_individual_files']
        
        # Save individual CSV if enabled
        if write_individual:
            save_csv(master_rows, "output_page_ocr.csv", csv_headers)
        
        # Save master CSV
        master_csv_path = save_csv(master_rows, "output_master_ocr.csv", csv_headers)
        
        print(f"\nCSV files saved:")
        if write_individual:
            print(f"- Individual: data/output/output_page_ocr.csv")
        print(f"- Master: {master_csv_path}")
    else:
        print("No data found across all files")

if __name__ == "__main__":
    main()