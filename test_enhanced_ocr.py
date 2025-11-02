#!/usr/bin/env python3
"""
Quick test of enhanced OCR on a few sample files
"""

from enhanced_ocr_processor import EnhancedOCRProcessor
from pathlib import Path
import sys

def main():
    processor = EnhancedOCRProcessor()
    
    # Test on first 3 images
    test_files = [
        Path('custody_screenshots/2025-01-08(149).png'),
        Path('custody_screenshots/2025-01-08(151).png'),
        Path('custody_screenshots/2025-01-08(150).png'),
    ]
    
    print("=== TESTING ENHANCED OCR ===\n")
    
    for img_path in test_files:
        if not img_path.exists():
            print(f"Skipping {img_path} (not found)")
            continue
            
        print(f"\n{'='*80}")
        print(f"Processing: {img_path.name}")
        print(f"{'='*80}\n")
        
        result = processor.process_image(img_path)
        
        if result:
            print(f"✅ Success!")
            print(f"Sender: {result['sender']}")
            print(f"Recipient: {result['recipient']}")
            print(f"Text length: {result['char_count']} chars")
            print(f"\nFormatted Text Preview (first 500 chars):")
            print("-" * 80)
            print(result['formatted_text'][:500])
            print("-" * 80)
        else:
            print(f"❌ Failed to process")
    
    print(f"\n{'='*80}")
    print("Test complete! If results look good, run RUN_ENHANCED_OCR.bat")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()
