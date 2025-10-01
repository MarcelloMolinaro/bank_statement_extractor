# Bank Statement Extractor

A Python tool that extracts transactions from PDF bank statements and exports them to CSV format. Supports batch processing of multiple PDFs with intelligent categorization and configurable output options.

## Features

- **Batch Processing**: Process multiple PDF files in a directory
- **Smart Parsing**: Handles QR code noise and multi-line transaction descriptions
- **Auto-categorization**: Categorizes transactions based on description keywords
- **Flexible Output**: Generate individual CSVs per statement or a master CSV
- **Configurable**: YAML-based configuration for easy customization
- **Date Detection**: Automatically extracts statement year from filename

## Installation & Quick Start

```bash
# Clone or download the project
cd bank_statement_extractor

# Setup environment and install dependencies
./build.sh

# Place PDF files in the statements/ directory
# (Optional) Configure settings in config.yml

# Run the extractor
./run.sh
```

That's it! The script will process all PDFs in the `statements/` directory and generate CSV files in the `output/` directory.

## Configuration

Edit `config.yml` to customize behavior:

```yaml
# PDF directory path
paths:
  pdf_path: "./statements/"

# Account information
account:
  account_name: "Your Bank"
  account_type: "Checking"

# Transaction categorization rules
categories:
  "INTEREST CREDIT": "Income/Interest Income"
  "PAYROLL": "Income/Salary"
  "TRANSFER": "Transfer"
  "VENMO": "Transfer"
  "AMAZON": "Shopping"
  "STARBUCKS": "Food & Dining"
  # Add your own rules...

# CSV output options
csv:
  headers: ["Date", "Account", "Description", "Check #", "Category", "Credit", "Debit", "Account Name"]
  write_individual_files: false  # Set to true for per-statement CSVs
```

## Usage

### Basic Usage
```bash
# Process all PDFs in statements/ directory
./run.sh
```

### Manual Setup (Alternative)
```bash
# If you prefer manual setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/extract.py
```

### Output Files
- **`output/output_master.csv`**: Combined transactions from all statements
- **`output/output_YYYY-MM.csv`**: Individual statement files (if enabled in config)

### CSV Format
| Date | Account | Description | Check # | Category | Credit | Debit | Account Name |
|------|---------|-------------|---------|----------|--------|-------|--------------|
| 12/15/2022 | Student Checking | PREAUTHORIZED CREDIT MOZART DATA... | | Income/Salary | 2509.75 | | M_wintrust |

## Supported PDF Formats

- **Wintrust Bank statements** (tested)
- **Transaction Detail sections** with date/description/amount format
- **Multi-page statements** with continuation handling
- **QR code noise filtering** for clean extraction

## File Structure

```
bank_statement_extractor/
├── src/
│   └── extract.py          # Main extraction script
├── statements/             # Place PDF files here
├── output/                 # Generated CSV files
│   ├── output_master.csv
│   └── output_YYYY-MM.csv
├── config.yml             # Configuration file
├── requirements.txt       # Python dependencies
├── build.sh              # Setup script
├── run.sh                # Execution script
└── README.md             # This file
```

## Advanced Usage

### Custom Categories
Add new categorization rules in `config.yml`:
```yaml
categories:
  "YOUR KEYWORD": "Your Category"
  "VENMO": "Transfer"
  "SCHWAB": "Investments"
```

### Individual vs Master CSV
- **Master only** (default): `write_individual_files: false`
- **Both**: `write_individual_files: true`

### PDF Filename Format
Expected format: `*-DD-Mon-YYYY.pdf`
- Example: `002-0000002300040174-15-Dec-2022.pdf`
- Year is auto-detected from filename

## Troubleshooting

### No transactions extracted
- Check if PDF contains "Transaction Detail" section
- Verify PDF is text-based (not scanned image)
- Try enabling debug output in the script

### Missing transaction descriptions
- The parser handles multi-line descriptions automatically
- QR code noise is filtered out
- Check if continuation lines are being captured

### Configuration issues
- Ensure `config.yml` is valid YAML
- Check file paths are correct
- Verify all required sections are present

## Dependencies

- `pdfplumber`: PDF text extraction
- `pandas`: Data manipulation
- `PyYAML`: Configuration file parsing
- `python-dateutil`: Date parsing
- `click`: Command-line interface (legacy)

## License

This project is for personal use. Modify and distribute as needed.