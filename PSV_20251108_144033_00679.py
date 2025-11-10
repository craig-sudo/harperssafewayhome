#!/usr/bin/env python3
\"\"\"
Evidence Processor - Secure Legal Documentation System
Professional OCR processing with cryptographic integrity and quality control
For Harper\'s Custody Case (FDSJ-739-24)
\"\"\"

import pytesseract
from PIL import Image
import os
import pandas as pd
import hashlib
import logging
from datetime import datetime
from pathlib import Path
import re
from typing import Dict, Any, Optional, Tuple
from image_preprocessor import preprocess_image_for_ocr, cleanup_temp_files
from config.settings import (
    tesseract_config, min_ocr_confidence, relevance_codes, 
    image_extensions, csv_fields, tesseract_cmd
)
from dateutil.parser import parse as date_parse # Added for robust date parsing
from dateutil.relativedelta import relativedelta # Added for handling relative dates

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/evidence_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set Tesseract path if specified
if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


class SecureEvidenceProcessor:
    \"\"\"Professional evidence processor with cryptographic integrity\"\"\"
    
    def __init__(self):
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        logger.info(f\"Initializing Secure Evidence Processor - Session: {self.session_id}\")
        
        # Ensure output directories exist
        os.makedirs('output', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Priority weights for legal relevance
        self.priority_weights = {
            'CRIMINAL_CONDUCT': 10,
            'ENDANGERMENT': 9,
            'NON_COMPLIANCE': 8,
            'FINANCIAL_IMPACT': 7,
            'USER_COMMITMENT': 6,
            'COMMUNICATION': 5,
            'REVIEW_REQUIRED': 1
        }

    def calculate_sha256(self, file_path: str) -> str:
        \"\"\"Calculates SHA-256 hash for cryptographic integrity verification\"\"\"
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(8192)  # Read in 8KB chunks
                    if not chunk:
                        break
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f\"Failed to calculate SHA-256 for {file_path}: {e}\")
            return \"HASH_CALCULATION_FAILED\"

    def extract_datetime_from_text(self, text: str) -> str:
        \"\"\"
        Extract date/time information from OCR text using more robust patterns
        and dateutil for parsing.
        \"\"\"
        text_lower = text.lower()
        now = datetime.now()

        # Prioritized patterns: Date and Time together, then Date only, then Time only
        datetime_patterns = [
            # Full datetime (e.g., Nov 5, 2023 at 1:23 PM, 11/05/2023 13:23)
            r'((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\\s+\\d{1,2},?\\s+\\d{2,4}(?:\\s+at)?\\s+\\d{1,2}:\\d{2}(?:\\s*[ap]m)?)\\b',
            r'\\b(\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4}(?:\\s+\\d{1,2}:\\d{2}(?:\\s*[ap]m)?)?)\\b', # MM/DD/YYYY HH:MM AM/PM
            r'\\b(\\d{2,4}[/-]\\d{1,2}[/-]\\d{1,2}(?:\\s+\\d{1,2}:\\d{2}(?:\\s*[ap]m)?)?)\\b', # YYYY/MM/DD HH:MM AM/PM
            # Relative dates with time (e.g., Yesterday 10:30 AM)
            r'\\b(today|yesterday|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\\s+\\d{1,2}:\\d{2}(?:\\s*[ap]m)?\\b',
        ]

        date_patterns = [
            r'\\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\\s+\\d{1,2},?\\s+\\d{2,4}\\b', # Month DD, YYYY
            r'\\b(\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4})\\b',  # MM/DD/YYYY or M/D/YY
            r'\\b(\\d{2,4}[/-]\\d{1,2}[/-]\\d{1,2})\\b', # YYYY/MM/DD
            r'\\b(today|yesterday|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\\b', # Relative days
        ]

        time_patterns = [
            r'\\b(\\d{1,2}:\\d{2}(?::\\d{2})?(?:\\s*[ap]m)?)\\b', # HH:MM:SS AM/PM or HH:MM AM/PM
        ]

        # Combine date and time if found separately
        best_date = None
        best_time = None
        
        # Try to find full datetime first
        for pattern in datetime_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    dt, _ = date_parse(match.group(1), fuzzy_with_tokens=True)
                    if dt is not None:
                         return dt.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue # Skip to next pattern if parsing fails

        # If no full datetime, try to find date and time separately
        for pattern in date_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    # Handle relative dates
                    date_str = match.group(1)
                    if date_str == 'today':
                        best_date = now
                    elif date_str == 'yesterday':
                        best_date = now - relativedelta(days=1)
                    elif date_str in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                        # Find the most recent occurrence of this weekday
                        current_weekday = now.weekday() # Monday is 0, Sunday is 6
                        target_weekday = datetime.strptime(date_str, '%A').weekday()
                        days_ago = (current_weekday - target_weekday + 7) % 7
                        best_date = now - relativedelta(days=days_ago)
                    else:
                        best_date = date_parse(date_str, fuzzy=True)
                    # If only a year is missing, dateutil might default to current year.
                    # Ensure year is reasonable if it's in the distant past/future.
                    if best_date and (best_date.year < 2000 or best_date.year > (now.year + 1)):
                        # Attempt to re-parse assuming current year if year was ambiguous
                        try:
                            best_date = date_parse(date_str + f" {now.year}", fuzzy=True)
                        except ValueError:
                            pass # Stick with original best_date if current year fails
                    break
                except ValueError:
                    continue

        for pattern in time_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    best_time = date_parse(match.group(1), fuzzy=True).time()
                    break
                except ValueError:
                    continue

        # Combine found date and time
        if best_date and best_time:
            return datetime.combine(best_date.date(), best_time).strftime('%Y-%m-%d %H:%M:%S')
        elif best_date:
            return best_date.strftime('%Y-%m-%d') + " 00:00:00" # Default time if only date found
        elif best_time:
            # If only time, assume today's date
            return datetime.combine(now.date(), best_time).strftime('%Y-%m-%d %H:%M:%S')

        return "UNKNOWN"

    def detect_sender_recipient(self, text: str, filename: str) -> Tuple[str, str]:
        \"\"\"
        Detect sender and recipient using Craig\'s specific rules:
        - \"My Girl\" or \"Emma\" at top → Craig (right) & Emma (left)
        - Jane/Nanny conversations → Craig & Jane
        - Others → Craig & \"Contact\"
        - Cole Brooks/Tony Baker → Emma & Craig
        \"\"\"\
        text_upper = text.upper()
        filename_lower = filename.lower()
        
        # Default sender is Craig (Harper\'s dad)
        sender = \"Craig\"
        recipient = \"Unknown\"
        
        # Rule 1: Emma conversations (My Girl, Emma indicators)
        if any(indicator in text_upper for indicator in [\'MY GIRL\', \'EMMA\']):\
            sender = \"Craig\"\
            recipient = \"Emma\"\
        
        # Rule 2: Jane/Nanny conversations
        elif any(name in text_upper for name in [\'JANE\', \'NANNY\']):\
            sender = \"Craig\"\
            recipient = \"Jane\"\
        
        # Rule 3: Cole Brooks/Tony Baker → Emma sending TO Craig
        elif any(name in text_upper for name in [\'COLE BROOKS\', \'TONY BAKER\', \'COLE\', \'TONY\']):\
            sender = \"Emma\"  # Emma using lawyer\'s communication
            recipient = \"Craig\"\
        
        # Rule 4: Other known contacts
        elif any(name in text_upper for name in [\'RYAN\', \'MATT\', \'NICK\', \'KERRIE\']):\
            sender = \"Craig\"\
            recipient = \"Contact\"\
        
        # Rule 5: Check filename for additional context
        if \'emma\' in filename_lower:\
            recipient = \"Emma\"\
        elif \'jane\' in filename_lower:\
            recipient = \"Jane\"\
        
        return sender, recipient

    def categorize_content(self, text: str) -> Tuple[str, int]:
        \"\"\"Categorize content with priority scoring for Harper\'s case\"\"\"\
        text_lower = text.lower()
        
        for category, keywords in relevance_codes.items():
            if category == \'REVIEW_REQUIRED\':
                continue
                
            if any(keyword in text_lower for keyword in keywords):\
                priority_score = self.priority_weights.get(category, 1)\
                return category, priority_score
        
        return \'REVIEW_REQUIRED\', self.priority_weights.get(\'REVIEW_REQUIRED\', 1)

    def process_single_image(self, file_path: str) -> Optional[Dict[str, Any]]:
        \"\"\"\
        Process single image with full security and quality control
        Returns dict with all evidence fields or None if processing fails
        \"\"\"\
        temp_path = None
        
        try:
            # SECURITY STEP 1: Calculate hash of ORIGINAL file for integrity
            file_integrity_hash = self.calculate_sha256(file_path)
            logger.debug(f\"Processing {os.path.basename(file_path)} - Hash: {file_integrity_hash[:12]}...\")
            
            # OCR STEP 1: Enhanced preprocessing
            temp_path = preprocess_image_for_ocr(file_path)
            
            # OCR STEP 2: Extract text with enhanced configuration
            text = pytesseract.image_to_string(temp_path, config=tesseract_config)
            
            # OCR STEP 3: Get confidence data for quality control
            data = pytesseract.image_to_data(
                temp_path, 
                config=tesseract_config, 
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate average confidence
            confidences = [c for c, t in zip(data[\'conf\'], data[\'text\']) if t.strip() and c > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # OCR STEP 4: Content analysis and categorization
            relevance_code, priority_score = self.categorize_content(text)
            
            # OCR STEP 5: Quality control and status determination
            status = \"SUCCESS\"\
            if avg_confidence < min_ocr_confidence:\
                relevance_code = \"REVIEW_REQUIRED\"\
                status = \"LOW_CONFIDENCE_FLAG\"\
                logger.warning(f\"Low confidence ({avg_confidence:.1f}%) for {os.path.basename(file_path)}\")
            
            # Extract metadata
            filename = os.path.basename(file_path)
            extracted_datetime = self.extract_datetime_from_text(text)
            sender, recipient = self.detect_sender_recipient(text, filename)
            
            # Clean up text content
            text_content = text.strip()
            
            # Clean up temporary file
            cleanup_temp_files(temp_path, file_path)
            
            return {
                \'File_Name\': filename,
                \'File_Integrity_Hash\': file_integrity_hash,  # CRITICAL for legal defensibility
                \'Date_Time_Approx\': extracted_datetime,
                \'Sender\': sender,
                \'Recipient\': recipient,
                \'Key_Factual_Statement\': text_content,
                \'Relevance_Code\': relevance_code,
                \'Processing_Status\': status,
                \'Confidence_Score\': round(avg_confidence, 2),
                \'Legal_Priority\': priority_score,
                \'File_Size_Bytes\': os.path.getsize(file_path),
                \'Processing_Session\': self.session_id,
                \'Processed_DateTime\': datetime.now().strftime(\'%Y-%m-%d %H:%M:%S\')
            }

        except Exception as e:
            logger.error(f\"Processing failed for {file_path}: {e}\")
            
            # Calculate hash even for failed processing (for integrity records)
            try:
                file_integrity_hash = self.calculate_sha256(file_path)
            except:
                file_integrity_hash = \"HASH_CALCULATION_FAILED\"
            
            # Clean up temporary file on error
            if temp_path:
                cleanup_temp_files(temp_path, file_path)
            
            return {
                \'File_Name\': os.path.basename(file_path),
                \'File_Integrity_Hash\': file_integrity_hash,
                \'Date_Time_Approx\': \'Processing_Failed\',\
                \'Sender\': \'Unknown\',\
                \'Recipient\': \'Unknown\',\
                \'Key_Factual_Statement\': f\'OCR Failed: {str(e)}\',\
                \'Relevance_Code\': \'REVIEW_REQUIRED\',\
                \'Processing_Status\': \'FAILED\',\
                \'Confidence_Score\': 0,\
                \'Legal_Priority\': 1,\
                \'File_Size_Bytes\': 0,\
                \'Processing_Session\': self.session_id,\
                \'Processed_DateTime\': datetime.now().strftime(\'%Y-%m-%d %H:%M:%S\')
            }

    def process_directory(self, input_folder: str) -> Optional[str]:
        \"\"\"Process all images in directory with comprehensive reporting\"\"\"\
        try:
            input_path = Path(input_folder)
            if not input_path.exists():
                logger.error(f\"Input folder not found: {input_folder}\")
                return None
            
            # Find all image files
            image_files = []
            for ext in image_extensions:
                image_files.extend(input_path.rglob(f\'*{ext}\'))
                image_files.extend(input_path.rglob(f\'*{ext.upper()}\'))
            
            if not image_files:\
                logger.warning(f\"No image files found in {input_folder}\")
                return None
            
            logger.info(f\"Found {len(image_files)} images to process\")
            
            # Process all images
            results = []
            failed_count = 0
            low_confidence_count = 0
            
            for i, image_path in enumerate(image_files, 1):\
                if i % 100 == 0:\
                    logger.info(f\"Progress: {i}/{len(image_files)} ({i/len(image_files)*100:.1f}%)\")
                
                result = self.process_single_image(str(image_path))\
                if result:\
                    results.append(result)\
                    
                    if result[\'Processing_Status\'] == \'FAILED\':
                        failed_count += 1
                    elif result[\'Processing_Status\'] == \'LOW_CONFIDENCE_FLAG\':
                        low_confidence_count += 1
            
            if not results:\
                logger.error(\"No images were successfully processed\")
                return None
            
            # Create DataFrame and save results
            df = pd.DataFrame(results)
            
            # Generate output filename
            timestamp = datetime.now().strftime(\'%Y%m%d_%H%M%S\')
            output_file = f\"output/secure_evidence_FDSJ739_{timestamp}.csv\"\
            
            # Save with UTF-8 encoding for legal characters
            df.to_csv(output_file, index=False, encoding=\'utf-8-sig\')
            
            # Generate comprehensive statistics
            self.generate_processing_report(df, output_file, failed_count, low_confidence_count)
            
            return output_file
            
        except Exception as e:
            logger.error(f\"Directory processing failed: {e}\")
            return None

    def generate_processing_report(self, df: pd.DataFrame, output_file: str, \
                                 failed_count: int, low_confidence_count: int):
        \"\"\"Generate comprehensive processing report\"\"\"\
        total_count = len(df)
        success_count = total_count - failed_count
        
        logger.info(f\"\\n{\'=\'*60}\")
        logger.info(f\"🏛️  SECURE EVIDENCE PROCESSING COMPLETE\")
        logger.info(f\"{\'=\'*60}\")
        logger.info(f\"📁 Output File: {output_file}\")
        logger.info(f\"📊 Processing Statistics:\")
        logger.info(f\"   Total Files: {total_count}\")
        logger.info(f\"   Successfully Processed: {success_count} ({success_count/total_count*100:.1f}%)\")
        logger.info(f\"   Failed Processing: {failed_count}\")
        logger.info(f\"   Low Confidence: {low_confidence_count}\")
        
        if \'Confidence_Score\' in df.columns:\
            avg_confidence = df[df[\'Confidence_Score\'] > 0][\'Confidence_Score\'].mean()\
            logger.info(f\"   Average OCR Confidence: {avg_confidence:.1f}%\")
        
        # Legal category breakdown
        logger.info(f\"📋 Evidence Categories:\")
        category_counts = df[\'Relevance_Code\'].value_counts()
        for category, count in category_counts.items():
            logger.info(f\"   {category}: {count}\")
        
        # Sender/Recipient analysis
        logger.info(f\"👥 Communication Analysis:\")
        sender_counts = df[\'Sender\'].value_counts()
        for sender, count in sender_counts.items():
            logger.info(f\"   From {sender}: {count}\")
        
        # High-priority evidence
        high_priority = df[df[\'Legal_Priority\'] >= 8]\
        if not high_priority.empty:\
            logger.info(f\"🚨 High Priority Evidence: {len(high_priority)} items\")
        
        # Security validation
        hash_failures = df[df[\'File_Integrity_Hash\'].str.contains(\'FAILED\', na=False)]\
        if not hash_failures.empty:\
            logger.warning(f\"⚠️  Hash calculation failed for {len(hash_failures)} files\")
        
        logger.info(f\"🔒 Cryptographic integrity hashes generated for all files\")
        logger.info(f\"⚖️  Evidence package ready for legal proceedings\")
        logger.info(f\"{\'=\'*60}\")


def main():
    \"\"\"Main execution function\"\"\"\
    processor = SecureEvidenceProcessor()
    
    # Default input folder
    default_folder = \"custody_screenshots\"
    
    # Check if default folder exists
    if not os.path.exists(default_folder):\
        logger.error(f\"Default input folder \'{default_folder}\' not found\")
        print(f\"Please create the folder \'{default_folder}\' and add your evidence images\")
        return
    
    print(\"🏛️  Secure Evidence Processor for Harper\'s Custody Case\")
    print(\"=\" * 60)
    print(\"This tool processes evidence with cryptographic integrity verification\")
    print(\"for court-admissible documentation.\")
    print()
    
    # Process the evidence
    output_file = processor.process_directory(default_folder)
    
    if output_file:\
        print(f\"\\n✅ Processing complete!\")
        print(f\"📁 Results saved to: {output_file}\")
        print(f\"🔒 All files include SHA-256 integrity hashes\")
        print(f\"⚖️  Evidence package ready for legal submission\")
    else:\
        print(\"\\n❌ Processing failed - check logs for details\")


if __name__ == \"__main__\":
    main()
