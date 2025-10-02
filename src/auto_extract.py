#!/usr/bin/env python3
"""
Smart PDF processor that automatically chooses between text extraction and OCR.
Tries text extraction first, falls back to OCR if needed.
"""

import os
import sys
import pdfplumber
from extract_pdf_text import main as text_extract_main
from extract_pdf_ocr import main as ocr_extract_main

def detect_pdf_type(pdf_path):
    """
    Detect if PDF contains extractable text or requires OCR.
    Returns: 'text' if extractable text found, 'ocr' if image-based
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Check first few pages for meaningful text
            pages_to_check = min(3, len(pdf.pages))
            total_text_length = 0
            
            for i in range(pages_to_check):
                text = pdf.pages[i].extract_text() or ""
                # Filter out common OCR artifacts and whitespace
                meaningful_text = ''.join(c for c in text if c.isalnum() or c.isspace())
                total_text_length += len(meaningful_text.strip())
            
            # If we found substantial text content, use text extraction
            # Threshold: at least 100 characters of meaningful text per page on average
            avg_text_per_page = total_text_length / pages_to_check
            
            if avg_text_per_page > 100:
                return 'text'
            else:
                return 'ocr'
                
    except Exception as e:
        print(f"Error analyzing PDF: {e}")
        return 'ocr'  # Default to OCR if analysis fails

def main():
    """Main entry point that auto-detects and processes PDFs."""
    print("🔍 Bank Statement Extractor")
    print("=" * 50)
    
    # Get PDF path from config or command line
    import yaml
    with open(os.path.join(os.path.dirname(__file__), '..', 'config.yml'), 'r') as f:
        config = yaml.safe_load(f)
    
    pdf_path = config['paths']['pdf_path']
    
    if os.path.isdir(pdf_path):
        # Process directory - analyze first PDF to determine method
        pdf_files = [f for f in os.listdir(pdf_path) if f.lower().endswith('.pdf')]
        if not pdf_files:
            print("❌ No PDF files found in directory")
            return
            
        # Test first PDF to determine extraction method
        first_pdf = os.path.join(pdf_path, sorted(pdf_files)[0])
        detection_result = detect_pdf_type(first_pdf)
        
        print(f"📄 Analyzing: {os.path.basename(first_pdf)}")
        print(f"🔧 Detection result: {detection_result.upper()}")
        
    else:
        # Single file
        detection_result = detect_pdf_type(pdf_path)
        print(f"📄 Analyzing: {os.path.basename(pdf_path)}")
        print(f"🔧 Detection result: {detection_result.upper()}")
    
    print("-" * 50)
    
    if detection_result == 'text':
        print("✅ Using TEXT EXTRACTION method...")
        text_extract_main()
    else:
        print("✅ Using OCR method...")
        ocr_extract_main()
    
    print("\n🎉 Processing complete!")

if __name__ == "__main__":
    main()
