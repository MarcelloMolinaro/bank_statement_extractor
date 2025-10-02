"""
Shared utilities for bank statement extraction.
"""
import os
import yaml
import csv
import re
from datetime import datetime

# Load configuration once
_config = None

def get_config():
    """Load and cache configuration."""
    global _config
    if _config is None:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yml')
        with open(config_path, 'r') as f:
            _config = yaml.safe_load(f)
    return _config

def extract_year_from_filename(filename):
    """Extract year from filename patterns."""
    # Try different patterns
    patterns = [
        r'(\d{4})',  # Any 4-digit year
        r'\b(\d{1,2})-(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-(\d{4})\b'  # DD-Mon-YYYY
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            # Return the year (last group for DD-Mon-YYYY, first group for simple year)
            groups = match.groups()
            return int(groups[-1]) if len(groups) > 1 else int(groups[0])
    
    return datetime.now().year

def categorize(desc):
    """Categorize transaction based on description."""
    config = get_config()
    d = desc.upper()
    for keyword in config['categories']:
        if keyword in d:
            return config['categories'][keyword]
    return ""

def save_csv(data, filename, headers):
    """Save data to CSV file."""
    config = get_config()
    output_dir = config['paths']['output_dir']
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    csv_path = os.path.join(output_dir, filename)
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
    
    return csv_path

def sort_transactions_by_date(transactions, date_key='Date'):
    """Sort transactions by date."""
    def parse_date_for_sorting(date_str):
        try:
            return datetime.strptime(date_str, "%m/%d/%Y")
        except:
            return datetime.min
    
    return sorted(transactions, key=lambda x: parse_date_for_sorting(x[date_key]))

def get_pdf_files(directory):
    """Get all PDF files from directory."""
    if os.path.isdir(directory):
        return [os.path.join(directory, name) 
                for name in sorted(os.listdir(directory)) 
                if name.lower().endswith(".pdf")]
    else:
        return [directory] if directory.lower().endswith(".pdf") else []

def format_date_with_year(date_str, year):
    """Format MM/DD date string with year."""
    if date_str and '/' in date_str:
        try:
            month, day = date_str.split('/')
            dt = datetime(year, int(month), int(day))
            return dt.strftime("%m/%d/%Y")
        except:
            return date_str
    return date_str
