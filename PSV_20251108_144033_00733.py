#!/usr/bin/env python3
"""
Smart OCR Processor - Adaptive Enhancement
Applies preprocessing only when it improves results
"""

import os
import cv2
import numpy as np
import pytesseract
from PIL import Image
import logging
import pandas as pd
from datetime import datetime
import hashlib
import re
from pathlib import Path

# Configure Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class SmartOCRProcessor:
    def __init__(self):
        self.setup_logging()
        self.results = []
        self.stats = {
            'total_processed': 0,
            'original_better': 0,
            'enhanced_better': 0,
            'failed_extractions': 0,
            'improvement_rate': 0.0
        }
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        os.makedirs('logs', exist_ok=True)
        log_file = f'logs/smart_ocr_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def apply_conservative_enhancement(self, image):
        """Apply minimal, careful enhancement"""
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Very gentle noise reduction
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            
            # Slight contrast enhancement only
            enhanced = cv2.convertScaleAbs(denoised, alpha=1.1, beta=5)
            
            # Gentle sharpening kernel
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(enhanced, -1, kernel)
            
            return sharpened
            
        except Exception as e:
            self.logger.warning(f"Enhancement failed: {e}")
            return image
            
    def extract_text_with_confidence(self, image):
        """Extract text and calculate confidence"""
        try:
            # Get OCR data with confidence
            data = pytesseract.image_to_data(
                image, 
                config='--oem 3 --psm 6 -l eng --dpi 300',
                output_type=pytesseract.Output.DICT
            )
            
            # Extract text
            text = pytesseract.image_to_string(
                image,
                config='--oem 3 --psm 6 -l eng --dpi 300'
            ).strip()
            
            # Calculate confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return text, avg_confidence
            
        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
            return "", 0.0
            
    def detect_sender_recipient(self, text, filename):
        """Enhanced sender/recipient detection with Craig mapping"""
        sender = "Unknown"
        recipient = "Unknown"
        
        # Craig-specific patterns (Harper's dad)
        craig_patterns = [
            r"Craig.*?(?:says?|said|writes?|wrote|texts?|texted)",
            r"(?:from|by)\s+Craig",
            r"Craig\s*:",
            r"^Craig\b",
            r"Dad.*?(?:says?|said|writes?|wrote|texts?|texted)",
            r"Harper'?s\s+(?:dad|father)"
        ]
        
        # Emma patterns (problematic mother)
        emma_patterns = [
            r"Emma.*?(?:says?|said|writes?|wrote|texts?|texted)",
            r"(?:from|by)\s+Emma",
            r"Emma\s*:",
            r"^Emma\b",
            r"Mom.*?(?:says?|said|writes?|wrote|texts?|texted)",
            r"Harper'?s\s+(?:mom|mother)"
        ]
        
        # Jane patterns (nanny/caregiver)
        jane_patterns = [
            r"Jane.*?(?:says?|said|writes?|wrote|texts?|texted)",
            r"(?:from|by)\s+Jane",
            r"Jane\s*:",
            r"^Jane\b",
            r"(?:nanny|caregiver|babysitter).*?Jane"
        ]
        
        text_lower = text.lower()
        
        # Check for Craig patterns
        for pattern in craig_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                sender = "Craig (Harper's Dad)"
                break
                
        # Check for Emma patterns
        for pattern in emma_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                if sender == "Unknown":
                    sender = "Emma (Problematic Mother)"
                else:
                    recipient = "Emma (Problematic Mother)"
                break
                
        # Check for Jane patterns
        for pattern in jane_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                if sender == "Unknown":
                    sender = "Jane (Nanny)"
                else:
                    recipient = "Jane (Nanny)"
                break
                
        # Fallback: use filename context
        if sender == "Unknown":
            filename_lower = filename.lower()
            if any(word in filename_lower for word in ['craig', 'dad', 'father']):
                sender = "Craig (Harper's Dad)"
            elif any(word in filename_lower for word in ['emma', 'mom', 'mother']):
                sender = "Emma (Problematic Mother)"
            elif any(word in filename_lower for word in ['jane', 'nanny']):
                sender = "Jane (Nanny)"
            else:
                sender = "Contact"
                
        if recipient == "Unknown":
            recipient = "Harper/Family"
            
        return sender, recipient
        
    def analyze_content_legally(self, text):
        """Legal content analysis for Harper's case"""
        categories = []
        
        # Financial/child support issues
        financial_keywords = [
            'money', 'child support', 'payment', 'financial', 'cost', 'expense',
            'bill', 'invoice', 'debt', 'owe', 'paid', 'cash', 'bank'
        ]
        
        # Substance abuse indicators
        substance_keywords = [
            'drink', 'drinking', 'drunk', 'alcohol', 'beer', 'wine', 'weed',
            'marijuana', 'drugs', 'high', 'party', 'hangover', 'substance'
        ]
        
        # Parenting/custody violations
        custody_keywords = [
            'custody', 'visitation', 'parenting', 'drop off', 'pick up',
            'schedule', 'weekend', 'holiday', 'vacation', 'court order'
        ]
        
        # Threatening/harassment
        threat_keywords = [
            'threat', 'threatening', 'harass', 'abuse', 'violent', 'angry',
            'rage', 'fuck you', 'hate', 'revenge', 'get back at'
        ]
        
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in financial_keywords):
            categories.append('Financial')
            
        if any(keyword in text_lower for keyword in substance_keywords):
            categories.append('Substance_Related')
            
        if any(keyword in text_lower for keyword in custody_keywords):
            categories.append('Custody_Related')
            
        if any(keyword in text_lower for keyword in threat_keywords):
            categories.append('Threatening')
            
        if not categories:
            categories.append('General')
            
        return '; '.join(categories)
        
    def process_single_file(self, file_path):
        """Process a single image with smart enhancement"""
        try:
            # Load image
            image = cv2.imread(str(file_path))
            if image is None:
                self.logger.warning(f"Could not load image: {file_path}")
                return None
                
            # Extract with original image
            original_text, original_confidence = self.extract_text_with_confidence(image)
            
            # Try conservative enhancement
            enhanced_image = self.apply_conservative_enhancement(image)
            enhanced_text, enhanced_confidence = self.extract_text_with_confidence(enhanced_image)
            
            # Choose best result
            if enhanced_confidence > original_confidence and len(enhanced_text) >= len(original_text) * 0.8:
                # Enhanced is better
                best_text = enhanced_text
                best_confidence = enhanced_confidence
                method_used = "Conservative Enhancement"
                self.stats['enhanced_better'] += 1
                improvement = enhanced_confidence - original_confidence
            else:
                # Original is better
                best_text = original_text
                best_confidence = original_confidence
                method_used = "Original (No Preprocessing)"
                self.stats['original_better'] += 1
                improvement = 0
                
            # Detect sender/recipient
            sender, recipient = self.detect_sender_recipient(best_text, file_path.name)
            
            # Analyze content
            categories = self.analyze_content_legally(best_text)
            
            # Create integrity hash
            integrity_hash = hashlib.sha256(best_text.encode()).hexdigest()[:16]
            
            # Build result
            result = {
                'filename': file_path.name,
                'file_path': str(file_path),
                'extracted_text': best_text,
                'confidence_score': round(best_confidence, 2),
                'text_length': len(best_text),
                'sender': sender,
                'recipient': recipient,
                'content_categories': categories,
                'method_used': method_used,
                'improvement': round(improvement, 2),
                'extraction_timestamp': datetime.now().isoformat(),
                'integrity_hash': integrity_hash,
                'file_size_kb': round(file_path.stat().st_size / 1024, 2)
            }
            
            self.stats['total_processed'] += 1
            
            if best_confidence < 50:
                self.stats['failed_extractions'] += 1
                self.logger.warning(f"Low confidence ({best_confidence:.1f}%): {file_path.name}")
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {e}")
            return None
            
    def process_directory(self, directory_path, max_files=None):
        """Process all images in directory"""
        directory = Path(directory_path)
        
        # Find all images
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
        all_images = []
        
        for ext in image_extensions:
            all_images.extend(directory.rglob(f'*{ext}'))
            all_images.extend(directory.rglob(f'*{ext.upper()}'))
            
        if max_files:
            all_images = all_images[:max_files]
            
        self.logger.info(f"🎯 SMART OCR PROCESSOR STARTING")
        self.logger.info(f"Found {len(all_images)} images to process")
        
        # Process each image
        for i, image_path in enumerate(all_images, 1):
            self.logger.info(f"Processing {i}/{len(all_images)}: {image_path.name}")
            
            result = self.process_single_file(image_path)
            if result:
                self.results.append(result)
                
            # Progress updates
            if i % 100 == 0:
                self.logger.info(f"Progress: {i}/{len(all_images)} ({i/len(all_images)*100:.1f}%)")
                
        # Calculate final stats
        if self.stats['total_processed'] > 0:
            self.stats['improvement_rate'] = (self.stats['enhanced_better'] / 
                                            self.stats['total_processed']) * 100
                                            
        self.save_results()
        self.print_final_stats()
        
    def save_results(self):
        """Save results to CSV"""
        if not self.results:
            self.logger.warning("No results to save")
            return
            
        # Create output directory
        os.makedirs('output', exist_ok=True)
        
        # Generate timestamp filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f'output/smart_ocr_results_{timestamp}.csv'
        
        # Save to CSV
        df = pd.DataFrame(self.results)
        df.to_csv(csv_filename, index=False)
        
        self.logger.info(f"✅ Results saved to: {csv_filename}")
        
    def print_final_stats(self):
        """Print comprehensive final statistics"""
        print(f"\n{'='*60}")
        print(f"🎯 SMART OCR PROCESSING COMPLETE!")
        print(f"{'='*60}")
        print(f"Total files processed: {self.stats['total_processed']:,}")
        print(f"Original method better: {self.stats['original_better']:,} ({self.stats['original_better']/self.stats['total_processed']*100:.1f}%)")
        print(f"Enhanced method better: {self.stats['enhanced_better']:,} ({self.stats['enhanced_better']/self.stats['total_processed']*100:.1f}%)")
        print(f"Failed extractions (< 50% confidence): {self.stats['failed_extractions']:,}")
        print(f"Enhancement improvement rate: {self.stats['improvement_rate']:.1f}%")
        print(f"Success rate: {((self.stats['total_processed'] - self.stats['failed_extractions'])/self.stats['total_processed']*100):.1f}%")
        print(f"{'='*60}")

if __name__ == "__main__":
    processor = SmartOCRProcessor()
    
    # Process evidence directory
    evidence_dir = "custody_screenshots"
    
    print("🔍 Smart OCR Processor - Adaptive Enhancement")
    print("Applies preprocessing only when it improves results")
    print(f"Processing directory: {evidence_dir}")
    
    processor.process_directory(evidence_dir, max_files=1000)  # Test with 1000 files first