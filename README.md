# Bank Statement Extractor

A Python tool that extracts transactions from PDF bank statements and exports them to CSV format. Supports both text-based and image-based PDFs with intelligent auto-detection, batch processing, and configurable output options.

## Features

- **🤖 Auto-Detection**: Automatically chooses between text extraction and OCR
- **📄 Dual Processing**: Handles both text-based and scanned/image PDFs
- **🔍 OCR Support**: Advanced optical character recognition for image-based statements
- **📊 Batch Processing**: Process multiple PDF files in a directory
- **🧠 Smart Parsing**: Handles QR code noise and multi-line transaction descriptions
- **🏷️ Auto-categorization**: Categorizes transactions based on description keywords
- **📁 Flexible Output**: Generate individual CSVs per statement or a master CSV
- **⚙️ Configurable**: YAML-based configuration for easy customization
- **📅 Date Detection**: Automatically extracts statement year from filename
- **📋 Date Sorting**: All transactions are sorted chronologically

## Installation & Quick Start

```bash
# Clone or download the project
cd bank_statement_extractor

# Setup environment and install dependencies
./scripts/build.sh

# Place PDF files in the data/statements/ directory
# (Optional) Configure settings in config.yml

# Run the extractor
./scripts/run.sh
```

That's it! The script will automatically detect the best extraction method, process all PDFs in the `data/statements/` directory, and generate CSV files in the `data/output/` directory.

## How It Works

The tool automatically analyzes your PDFs and chooses the best extraction method:

1. **Text Extraction** (Fast): For digital PDFs with selectable text
2. **OCR Extraction** (Slower): For scanned or image-based PDFs

No need to choose - it just works!

## Configuration

Edit `config_example.yml` to customize behavior and rename to `config.yml`:

```yaml
# PDF directory path
paths:
  pdf_path: "./data/statements/"

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

### Basic Usage
```bash
# Auto-detect and process all PDFs
./scripts/run.sh
```

### Manual Setup (Alternative)
```bash
# If you prefer manual setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/auto_extract.py
```

### Output Files
- **`data/output/output_master_text.csv`**: Combined transactions from text-based PDFs
- **`data/output/output_master_ocr.csv`**: Combined transactions from image-based PDFs
- **`data/output/output_YYYY-MM.csv`**: Individual statement files (if enabled in config)

### CSV Format

**Text Extraction Output:**
| Date | Account | Description | Check # | Category | Credit | Debit | Account Name |
|------|---------|-------------|---------|----------|--------|-------|--------------|
| 12/25/2024 | Checking | PAYROLL DEPOSIT | | Income/Salary | 2500.00 | | YOUR_BANK |

**OCR Extraction Output:**
| Date | Category | Description | Debit Amount | Credit Amount |
|------|----------|-------------|--------------|---------------|
| 12/25/2024 | Income/Salary | PAYROLL DEPOSIT | | $2,500.00 |

## Supported PDF Formats

### Text-Based PDFs (Fast Processing)
- **Digital bank statements** with selectable text
- **Wintrust Bank statements** (tested)
- **Transaction Detail sections** with date/description/amount format
- **Multi-page statements** with continuation handling
- **QR code noise filtering** for clean extraction

### Image-Based PDFs (OCR Processing)
- **Scanned bank statements**
- **Image-based PDFs** without selectable text
- **Amalgamated Bank statements** (tested)
- **Multi-page OCR** with cross-page continuation handling
- **Smart page detection** (skips pages without transaction data)

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

## Advanced Usage

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

### PDF Filename Formats
The tool supports various filename formats and automatically extracts years:

**Text Extraction:**
- Format: `*-DD-Mon-YYYY.pdf`
- Example: `002-0000002300040174-15-Dec-2022.pdf`

**OCR Extraction:**
- Format: `*_MM_DD_YYYY_*.pdf`
- Example: `3_29_2024_amalgamated.pdf`

## Troubleshooting

### No transactions extracted
- Run `./scripts/run.sh` - the tool automatically detects the best extraction method
- Check if PDF contains "Transaction Detail" or "Activity Description" sections
- Verify PDF files are in the `data/statements/` directory
- For debugging, you can run the specific extraction methods manually:
  - `python src/extract_pdf_text.py` (for text-based PDFs)
  - `python src/extract_pdf_ocr.py` (for image-based PDFs)

### Missing transaction descriptions
- The parser handles multi-line descriptions automatically
- QR code noise is filtered out
- OCR handles cross-page continuations
- Check if continuation lines are being captured

### OCR-specific issues
- **Slow processing**: OCR is inherently slower than text extraction
- **Missing data**: Check Y-coordinate filtering in the OCR script
- **Garbled text**: Try adjusting OCR DPI settings (currently 300)

### Configuration issues
- Ensure `config.yml` is valid YAML
- Check file paths are correct
- Verify all required sections are present

## Dependencies

### Core Dependencies
- `pdfplumber`: PDF text extraction
- `pandas`: Data manipulation and CSV output
- `PyYAML`: Configuration file parsing

### OCR Dependencies (auto-installed)
- `pytesseract`: Python wrapper for Tesseract OCR
- `opencv-python`: Image processing for OCR
- `PyMuPDF` (fitz): PDF rendering to images
- `Pillow`: Image manipulation
- `numpy`: Numerical operations

### System Dependencies
- `tesseract`: OCR engine (installed via conda during setup)

## Privacy & Security

- **PDF files are ignored by git**: Your bank statements stay private
- **Local processing**: All data stays on your machine
- **No network calls**: Tool works completely offline

## License

This project is for personal use. Modify and distribute as needed.