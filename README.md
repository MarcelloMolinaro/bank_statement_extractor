# Bank Statement Extractor

A Python tool that extracts transactions from PDF bank statements and exports them to CSV format.

## Key Features

- **Auto-Detection**: Automatically chooses between text extraction and OCR
- **Batch Processing**: Process multiple PDF files in a directory
- **🏷️ Categorization**: Categorizes transactions based on user-specified keywords
- **⚙️ Configurable**: YAML-based configuration for easy customization

- **Text-based PDFs** (fast): Digital statements with selectable text - *Tested: Wintrust Bank*
- **Image-based PDFs** (slower): Scanned statements requiring OCR - *Tested: Amalgamated Bank*


## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/MarcelloMolinaro/bank_statement_extractor.git
cd bank_statement_extractor

# 2. Setup (one time)
./scripts/build.sh

# 3. Add your PDFs to data/statements/

# 4. Run the extractor
./scripts/run.sh
```

That's it!

## ⚙️ Configuration

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
├── config_example.yml           # Example configuration, rename to config.yml
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

### OCR Coordinate Configuration
For different bank layouts, adjust OCR X-coordinates in `config.yml`:
```yaml
ocr:
  x_ranges:
    Date: [135, 296]      # X pixels for date column
    Description: [296, 1643]  # X pixels for description column
    Credit: [1643, 2052]  # X pixels for credit column
    Debit: [2052, 2470]   # X pixels for debit column
```

### PDF Date Formats
- The tool extracts the year from the filename, defaulting to current year when no
4 digit year is  found.
- The date formatting for dates within statements liekly doesn't capture all date formats
- Room for improvement here!

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
- **Incorrect data**: See OCR  X-Coordinate Configuration above

### Configuration issues
- If you changed the csv_headers at all, you might need to re-map any new fields in the .py files

### System Dependencies
- `tesseract`: OCR engine (must be installed via conda during setup)
- ... this worked... but Brew should work as well
```bash
conda install -c conda-forge tesseract-data-eng
```

## Future updates
- Dynamic OCR coordinate recognition (X and Y)
- Dynamic CSV Header generation based on transaction content
- Dynamic page skipping when transaction data is not present
- Better date parsing

## Privacy & Security

- **PDF files are ignored by git**: Your bank statements stay private
- **Local processing**: All data stays on your machine
- **No network calls**: Tool works completely offline

## License

This project is for personal use. Modify and distribute as needed.
Please comment if it was helupful to you and open an issue or PR if you want any changes or additions!