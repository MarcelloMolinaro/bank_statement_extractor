# Bank Statement Extractor

A Python tool that extracts transactions from PDF bank statements and exports them to CSV format. Automatically detects whether to use text extraction or OCR based on PDF content.

## Features

- **🤖 Auto-Detection**: Automatically chooses between text extraction and OCR
- **📄 Dual Processing**: Handles both text-based and scanned PDFs
- **📊 Batch Processing**: Process multiple PDF files in a directory
- **🏷️ Auto-categorization**: Categorizes transactions based on keywords
- **⚙️ Configurable**: YAML-based configuration for easy customization
- **📋 Date Sorting**: All transactions are sorted chronologically

**Tested with:** Wintrust Bank (text extraction) and Amalgamated Bank (OCR extraction)

## Quick Start

```bash
# 1. Setup (one time)
./scripts/build.sh

# 2. Add your PDFs to data/statements/

# 3. Run the extractor
./scripts/run.sh
```

That's it! The tool automatically detects the best extraction method and processes all PDFs.

## How It Works

The tool automatically analyzes your PDFs and chooses the best extraction method:

1. **Text Extraction** (Fast): For digital PDFs with selectable text
2. **OCR Extraction** (Slower): For scanned or image-based PDFs

No need to choose - it just works!

## Configuration

Edit `config_example.yml` to customize behavior and rename to `config.yml`:

```yaml
# Directory paths
paths:
  pdf_path: "./data/statements/"
  output_dir: "data/output"

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
  ocr_headers: ["Date", "Category", "Description", "Debit Amount", "Credit Amount"]
  write_individual_files: false  # Set to true for per-statement CSVs
```

## Usage

```bash
# Normal usage
./scripts/run.sh

# Manual setup (if needed)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/auto_extract.py
```

### Output Files & Formats
CSV files are saved to `data/output/` directory by default.
CSV formats can be modified in the `config.yml`


## Supported PDF Formats

- **Text-based PDFs** (fast): Digital statements with selectable text - *Tested: Wintrust Bank*
- **Image-based PDFs** (slower): Scanned statements requiring OCR - *Tested: Amalgamated Bank*

## File Structure

```
bank_statement_extractor/
├── src/
│   ├── auto_extract.py           # Auto-detection (main entry point)
│   ├── extract_pdf_text.py       # Text extraction engine
│   └── extract_pdf_ocr.py        # OCR extraction engine
├── scripts/
│   ├── build.sh                  # Setup script
│   └── run.sh                    # Execution script
├── data/
│   ├── statements/               # Place PDF files here
│   └── output/                   # Generated CSV files
│       ├── output_master_text.csv
│       └── output_master_ocr.csv
├── config.yml                   # Configuration file
├── config_example.yml           # Example configuration
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Advanced Usage & Configuration

### Custom Categories
Add new categorization rules in `config.yml`:
```yaml
categories:
  "YOUR KEYWORD": "Your Category"
  "VENMO": "Transfer"
  "SCHWAB": "Investments"
  "UBER": "Transportation"
```

### Individual vs Master CSV
- **Master only** (default): `write_individual_files: false`
- **Both**: `write_individual_files: true`

### OCR Coordinate Configuration
For different bank layouts, adjust OCR coordinates in `config.yml`:
```yaml
ocr:
  x_ranges:
    Date: [135, 296]      # X pixels for date column
    Description: [296, 1643]  # X pixels for description column
    Credit: [1643, 2052]  # X pixels for credit column
    Debit: [2052, 2470]   # X pixels for debit column
```

### PDF Filename Formats
The tool supports various filename formats and automatically extracts years:

**Text Extraction:**
- Default Format: `*-DD-Mon-YYYY.pdf`
- Example: `001-0000005500070237-15-Dec-2022.pdf`

**OCR Extraction:**
- Default Format: `*_MM_DD_YYYY_*.pdf`
- Example: `1_26_1986_monsters_midway.pdf`

## Troubleshooting

### No transactions extracted
- Check if PDF contains "Transaction Detail" (for Text based) or "Activity Description" (for OCR) sections
- Verify PDF files are in the `data/statements/` directory
- For debugging, you can run the specific extraction methods manually:
  - `python src/extract_pdf_text.py` (for text-based PDFs)
  - `python src/extract_pdf_ocr.py` (for image-based PDFs)

### Missing transaction descriptions
- Check if continuation lines are being captured
- OCR currently skips page 2 (no data found there)
- OCR Coordinate configs might need adjustment

### OCR-specific issues
- **Slow processing**: OCR is inherently slower than text extraction
- **Missing data**: Check Y-coordinate filtering in the OCR script
- **Garbled text**: Try adjusting OCR DPI settings (currently 300)
- **Incorrect data**: See OCR Coordinate Configuration above

### Configuration issues
- If you changed the csv_headers at all, you might need to re-map any new fields in the .py files

### System Dependencies
- `tesseract`: OCR engine (must be installed via conda during setup)
- ... this worked... but Brew should work as well
```bash
conda install -c conda-forge tesseract-data-eng
```

## Privacy & Security

- **PDF files are ignored by git**: Your bank statements stay private
- **Local processing**: All data stays on your machine
- **No network calls**: Tool works completely offline

## License

This project is for personal use. Modify and distribute as needed.