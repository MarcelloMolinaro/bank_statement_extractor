import re
from datetime import datetime
import pdfplumber
from extract_utils import get_config, categorize, save_csv, sort_transactions_by_date, get_pdf_files, extract_year_from_filename

# Transaction pattern
PATTERN = re.compile(r"^([A-Za-z]{3}\s?\d{1,2})\s+(.+?)\s+(-?\$[\d,]+\.\d{2})(?:\s+\$[\d,]+\.\d{2})?$")
MONTH_START = re.compile(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s?\d{1,2}\b", re.IGNORECASE)

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
        
        config = get_config()
        transactions.append({
            "Date": date_fmt,
            "Account": config['account']['account_type'],
            "Description": full_desc,
            "Check Number": check_no,
            "Category": categorize(full_desc),
            "Credit": credit,
            "Debit": debit,
            "Account Name": config['account']['account_name']
        })
        i = j
    
    return transactions

def process_pdf(single_pdf_path: str) -> list:
    """Process a single PDF file and return transactions."""
    config = get_config()
    statement_year = extract_year_from_filename(single_pdf_path)

    all_transactions = []
    with pdfplumber.open(single_pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            all_transactions.extend(extract_transactions_from_text(text, statement_year))

    # Write individual CSV only if enabled in config
    if config['csv']['write_individual_files']:
        fname = single_pdf_path.split('/')[-1].replace('.pdf', '')
        save_csv(all_transactions, f"output_{fname}.csv", config['csv']['headers'])

    return all_transactions

def main():
    """Main processing function."""
    config = get_config()
    pdf_files = get_pdf_files(config['paths']['pdf_path'])
    
    master_rows = []
    for pdf_file in pdf_files:
        master_rows.extend(process_pdf(pdf_file))

    if master_rows:
        # Sort transactions by date
        master_rows = sort_transactions_by_date(master_rows)
        
        # Save master CSV
        save_csv(master_rows, "output_master_text.csv", config['csv']['headers'])

if __name__ == "__main__":
    main()