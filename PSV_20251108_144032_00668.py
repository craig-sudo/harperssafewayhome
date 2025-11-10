#!/usr/bin/env python3
"""
Harper's Batch OCR Processor - Automated Evidence Processing
Processes organized evidence files and extracts text for court documentation
Case: FDSJ-739-24
"""

import pytesseract
from PIL import Image, ImageEnhance
import csv
import os
import sys
import logging
from datetime import datetime
from pathlib import Path
import re
from tqdm import tqdm
import pandas as pd

class BatchOCRProcessor:
    """Automated OCR processor for Harper's organized evidence files."""
    
    def __init__(self):
        """Initialize the batch OCR processor."""
        # Setup Tesseract path
        if os.path.exists(r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        
        # Initialize counters
        self.processed_count = 0
        self.error_count = 0
        self.text_extracted_count = 0
        
        # Setup folders
        self.organized_folder = Path("custody_screenshots_smart_renamed")
        self.output_folder = Path("output")
        self.output_folder.mkdir(exist_ok=True)
        
        # Initialize CSV file for results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_filename = self.output_folder / f"harper_ocr_results_{timestamp}.csv"
        
        # Setup logging
        log_folder = Path("logs")
        log_folder.mkdir(exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_folder / f"ocr_processing_{timestamp}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║              📄 HARPER'S BATCH OCR PROCESSOR 📄                  ║
║                                                                  ║
║  🔍 Automated Text Extraction from Organized Evidence Files     ║
║  📋 Case: FDSJ-739-24 | Court-Ready Documentation              ║
║                                                                  ║
║  📂 Processing: {self.organized_folder}                         ║
║  💾 Output: {self.csv_filename}                                 ║
╚══════════════════════════════════════════════════════════════════╝
        """)

    def enhance_image_for_ocr(self, image_path: Path) -> Image.Image:
        """Enhanced image preprocessing for better OCR results."""
        try:
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Enhance contrast and sharpness
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Convert to grayscale for better OCR
            image = image.convert('L')
            
            return image
            
        except Exception as e:
            self.logger.error(f"Error enhancing image {image_path}: {e}")
            return None

    def extract_text_from_image(self, image_path: Path) -> str:
        """Extract text from image using OCR."""
        try:
            # Enhance image first
            enhanced_image = self.enhance_image_for_ocr(image_path)
            if enhanced_image is None:
                return ""
            
            # Configure Tesseract for better text recognition
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?:;()[]{}/@#$%^&*-_+=<>|~`" \n\t'
            
            # Extract text
            text = pytesseract.image_to_string(enhanced_image, config=custom_config)
            
            # Clean up the text
            text = text.strip()
            text = re.sub(r'\n+', ' ', text)  # Replace multiple newlines with single space
            text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
            
            return text
            
        except Exception as e:
            self.logger.error(f"Error extracting text from {image_path}: {e}")
            return ""

    def analyze_content_priority(self, filename: str, text: str) -> tuple:
        """Analyze content for legal priority and categorization."""
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        priority = "MEDIUM"
        categories = []
        key_phrases = []
        
        # High priority indicators
        high_priority_keywords = [
            'threat', 'kill', 'hurt', 'harm', 'revenge', 'sorry', 'regret',
            'custody violation', 'contempt', 'emergency', 'police', 'arrest',
            'december 9', 'incident', 'harper', 'child', 'safety', 'welfare'
        ]
        
        # Category detection
        if 'threatening' in filename_lower or any(word in text_lower for word in ['threat', 'kill', 'hurt', 'harm']):
            categories.append('THREATENING_BEHAVIOR')
            priority = "HIGH"
        
        if 'custody-violation' in filename_lower or 'custody violation' in text_lower:
            categories.append('CUSTODY_VIOLATION')
            priority = "HIGH"
        
        if 'december-9' in filename_lower or 'december 9' in text_lower:
            categories.append('DECEMBER_9_INCIDENT')
            priority = "CRITICAL"
        
        if 'health-medical' in filename_lower or any(word in text_lower for word in ['doctor', 'medical', 'hospital', 'sick', 'injury']):
            categories.append('MEDICAL_EVIDENCE')
        
        if 'legal-court' in filename_lower or any(word in text_lower for word in ['court', 'judge', 'lawyer', 'custody agreement']):
            categories.append('LEGAL_PROCEEDINGS')
        
        if 'financial' in filename_lower or any(word in text_lower for word in ['money', 'support', 'payment', 'bank']):
            categories.append('FINANCIAL_EVIDENCE')
        
        # Extract key phrases
        for keyword in high_priority_keywords:
            if keyword in text_lower:
                key_phrases.append(keyword)
        
        # Check for people mentioned
        people_mentioned = []
        if 'emma' in filename_lower or 'emma' in text_lower:
            people_mentioned.append('Emma')
        if 'matt' in filename_lower or 'matt' in text_lower:
            people_mentioned.append('Matt')
        if 'cole' in filename_lower or 'cole' in text_lower:
            people_mentioned.append('Cole')
        if 'tony' in filename_lower or 'tony' in text_lower:
            people_mentioned.append('Tony')
        if 'harper' in filename_lower or 'harper' in text_lower:
            people_mentioned.append('Harper')
        
        return priority, categories, key_phrases, people_mentioned

    def process_all_organized_files(self):
        """Process all files in the organized folders."""
        self.logger.info("Starting batch OCR processing of organized evidence files...")
        
        # Initialize CSV file
        with open(self.csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'filename', 'folder_category', 'file_path', 'date_extracted', 
                'text_content', 'text_length', 'priority', 'categories', 
                'key_phrases', 'people_mentioned', 'processing_timestamp'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Process each category folder
            category_folders = [
                'conversations', 'threatening', 'december_9_incident', 
                'health_medical', 'legal_court', 'custody_violation',
                'financial', 'school_issues', 'general'
            ]
            
            total_files = 0
            # Count total files first
            for folder_name in category_folders:
                folder_path = self.organized_folder / folder_name
                if folder_path.exists():
                    total_files += len([f for f in folder_path.glob('*') if f.is_file()])
            
            print(f"\n🔍 Processing {total_files} organized evidence files...")
            
            with tqdm(total=total_files, desc="Extracting text") as pbar:
                for folder_name in category_folders:
                    folder_path = self.organized_folder / folder_name
                    if not folder_path.exists():
                        continue
                    
                    self.logger.info(f"Processing folder: {folder_name}")
                    
                    for file_path in folder_path.glob('*'):
                        if not file_path.is_file():
                            continue
                        
                        # Skip non-image files
                        if file_path.suffix.lower() not in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                            continue
                        
                        try:
                            # Extract text from image
                            text = self.extract_text_from_image(file_path)
                            
                            # Analyze content
                            priority, categories, key_phrases, people_mentioned = self.analyze_content_priority(
                                file_path.name, text
                            )
                            
                            # Extract date from filename
                            date_match = re.search(r'(\d{8})', file_path.name)
                            date_extracted = date_match.group(1) if date_match else "unknown"
                            
                            # Write to CSV
                            writer.writerow({
                                'filename': file_path.name,
                                'folder_category': folder_name,
                                'file_path': str(file_path),
                                'date_extracted': date_extracted,
                                'text_content': text[:1000] if text else "",  # Limit text length
                                'text_length': len(text),
                                'priority': priority,
                                'categories': '; '.join(categories),
                                'key_phrases': '; '.join(key_phrases),
                                'people_mentioned': '; '.join(people_mentioned),
                                'processing_timestamp': datetime.now().isoformat()
                            })
                            
                            self.processed_count += 1
                            if text:
                                self.text_extracted_count += 1
                                
                            pbar.set_description(f"Extracted: {self.text_extracted_count}")
                            
                        except Exception as e:
                            self.logger.error(f"Error processing {file_path}: {e}")
                            self.error_count += 1
                        
                        pbar.update(1)

    def generate_summary_report(self):
        """Generate a summary report of the processing results."""
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                    📊 PROCESSING COMPLETE! 📊                    ║
╚══════════════════════════════════════════════════════════════════╝

✅ FILES PROCESSED: {self.processed_count}
📄 TEXT EXTRACTED: {self.text_extracted_count}
❌ ERRORS: {self.error_count}

📋 RESULTS SAVED TO: {self.csv_filename}

🎯 This CSV contains all extracted text and can be:
   • Imported into Excel for analysis
   • Searched for specific content
   • Used for court documentation
   • Shared with legal counsel

📂 Next steps:
   • Review the CSV file for important evidence
   • Use filters to find threatening messages
   • Generate timeline reports for court
   • Extract key evidence for custody filing
        """)

def main():
    """Main function to run the batch OCR processor."""
    try:
        processor = BatchOCRProcessor()
        processor.process_all_organized_files()
        processor.generate_summary_report()
        
    except KeyboardInterrupt:
        print("\n🚫 Processing interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()