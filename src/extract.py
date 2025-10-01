import csv
import yaml
import os
import re
from datetime import datetime
import pdfplumber
import pandas as pd

# Load configuration
with open(os.path.join(os.path.dirname(__file__), '..', 'config.yml'), 'r') as f:
    config = yaml.safe_load(f)

# Transaction pattern
PATTERN = re.compile(r"^([A-Za-z]{3}\s?\d{1,2})\s+(.+?)\s+(-?\$[\d,]+\.\d{2})(?:\s+\$[\d,]+\.\d{2})?$")
MONTH_START = re.compile(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s?\d{1,2}\b", re.IGNORECASE)

def categorize(desc):
    """Categorize transaction based on description."""
    d = desc.upper()
    for keyword in config['categories']:
        if keyword in d:
            return config['categories'][keyword]
    return ""

def extract_transactions_from_text(text, statement_year):
    """Extract transactions from text content."""
    if "transaction detail" not in text.lower():
        return []
    
    lines = text.splitlines()
    start = next((i + 1 for i, l in enumerate(lines) if "transaction detail" in l.lower()), None)
    if not start:
        return []
    
    transactions = []
    i = start
    
    while i < len(lines):
        line = lines[i]
        if "ending balance" in line.lower():
            break
            
        # Trim QR code noise from line start
        ms = MONTH_START.search(line)
        if ms and ms.start() > 0:
            line = line[ms.start():]
            
        m = PATTERN.match(line.strip())
        if not m:
            i += 1
            continue
            
        date_str, desc, amt = m.groups()
        if "beginning balance" in desc.lower():
            i += 1
            continue
        
        # Get continuation lines
        continuation_parts = []
        j = i + 1
        while j < len(lines):
            nxt = lines[j].strip()
            if not nxt or MONTH_START.search(nxt) or "transaction detail" in nxt.lower():
                break
            if len(nxt) > 15 and nxt.count(' ') == 0 and re.match(r'^[A-Z0-9]+$', nxt):
                j += 1
                continue
            continuation_parts.append(nxt)
            j += 1
            
        full_desc = (desc + " " + " ".join(continuation_parts)).strip()
        
        # Parse date and amount
        date_norm = re.sub(r"^([A-Za-z]{3})(\d{1,2})$", r"\1 \2", date_str)
        dt = datetime.strptime(f"{date_norm} {statement_year}", "%b %d %Y")
        date_fmt = dt.strftime("%-m/%-d/%Y")
        
        amt_value = float(amt.replace("$", "").replace(",", ""))
        credit = amt_value if amt_value > 0 else ""
        debit = amt_value if amt_value < 0 else ""
        
        check_no = ""
        if full_desc.startswith("CHECK"):
            parts = full_desc.split()
            if len(parts) > 1 and parts[1].isdigit():
                check_no = parts[1]
        
        transactions.append({
            "Date": date_fmt,
            "Account": config['account']['account_type'],
            "Description": full_desc,
            "Check #": check_no,
            "Category": categorize(full_desc),
            "Credit": credit,
            "Debit": debit,
            "Account Name": config['account']['account_name']
        })
        i = j
    
    return transactions

def process_pdf(single_pdf_path: str) -> list:
    """Process a single PDF file and return transactions."""
    # Ensure output directory exists
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    fname = os.path.basename(single_pdf_path)
    mdate = re.search(r"\b(\d{1,2})-(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-(\d{4})\b", fname, re.IGNORECASE)
    
    if mdate:
        _, mon_abbr, year_str = mdate.groups()
        month_num = config['months'][mon_abbr.lower()]
        output_csv = os.path.join(output_dir, f"output_{year_str}-{month_num}.csv")
        statement_year = int(year_str)
    else:
        output_csv = os.path.join(output_dir, "output.csv")
        statement_year = datetime.now().year

    all_transactions = []
    with pdfplumber.open(single_pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            all_transactions.extend(extract_transactions_from_text(text, statement_year))

    # Write individual CSV only if enabled in config
    if config['csv']['write_individual_files']:
        headers = config['csv']['headers']
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for row in all_transactions:
                writer.writerow({key: row.get(key, "") for key in headers})

    return all_transactions

def main():
    """Main processing function."""
    pdf_path = config['paths']['pdf_path']
    master_rows = []
    
    if os.path.isdir(pdf_path):
        for name in sorted(os.listdir(pdf_path)):
            if name.lower().endswith(".pdf"):
                master_rows.extend(process_pdf(os.path.join(pdf_path, name)))
    else:
        master_rows.extend(process_pdf(pdf_path))

    # Write master CSV
    if master_rows:
        # Ensure output directory exists
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        headers = config['csv']['headers']
        master_csv_path = os.path.join(output_dir, "output_master.csv")
        with open(master_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for row in master_rows:
                writer.writerow({key: row.get(key, "") for key in headers})

if __name__ == "__main__":
    main()