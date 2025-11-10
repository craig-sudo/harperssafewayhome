#!/usr/bin/env python3
"""
Harper's Enhanced Quality Evidence Processor
Advanced OCR with Quality Control, Confidence Scoring, and Smart Categorization
Case: FDSJ-739-24 - Professional Legal Documentation System
"""

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import csv
import os
import sys
import logging
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import re
from typing import Dict, List, Tuple, Optional
from tqdm import tqdm
import pandas as pd
import statistics
import threading
import queue
import time
from utils.path_utils import ensure_long_path, safe_filename

class EnhancedQualityProcessor:
    """Enhanced OCR processor with quality control and advanced features."""
    
    def __init__(self):
        """Initialize the enhanced quality processor."""
        # Setup Tesseract with optimized configuration
        if os.path.exists(r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        
        # Advanced OCR configurations for different content types
        self.ocr_configs = {
            'standard': '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,!?;:()-[]{}@#$%&*+=<>/\\"\'',
            'phone_numbers': '--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789()- .',
            'dates': '--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789/- :AMPM',
            'text_messages': '--oem 3 --psm 6',
            'court_docs': '--oem 3 --psm 4'
        }
        
        # Quality thresholds
        self.min_confidence = 60.0
        self.min_text_length = 10
        self.suspicious_patterns = [
            r'[^\x00-\x7F]+',  # Non-ASCII characters
            r'(.)\1{5,}',       # Repeated characters
            r'^[^a-zA-Z0-9]*$', # Only special characters
        ]
        
        # Processing statistics
        self.stats = {
            'total_processed': 0,
            'high_quality': 0,
            'medium_quality': 0,
            'low_quality': 0,
            'failed': 0,
            'duplicates': 0,
            'categories': {}
        }
        
        # Initialize folders and files
        self.setup_directories()
        self.setup_logging()
        
        # Content categorization patterns
        self.category_patterns = {
            'threatening': [
                r'\b(threat|harm|hurt|kill|violence|revenge|get you|destroy|ruin)\b',
                r'\b(sorry you will be|gonna get|watch out|regret)\b'
            ],
            'custody_violation': [
                r'\b(custody|visitation|court order|parenting time|access)\b',
                r'\b(not letting|blocking|refusing|denied)\b'
            ],
            'financial': [
                r'\$[\d,]+|\b(money|payment|support|financial|bank|account)\b',
                r'\b(owe|debt|pay|cost|expense|bill)\b'
            ],
            'medical_health': [
                r'\b(doctor|hospital|medical|health|sick|injury|medicine|therapy)\b',
                r'\b(appointment|treatment|diagnosis|prescription)\b'
            ],
            'school_issues': [
                r'\b(school|teacher|principal|grade|homework|education|class)\b',
                r'\b(meeting|conference|problem|issue|behavior)\b'
            ],
            'legal_court': [
                r'\b(court|judge|lawyer|attorney|legal|hearing|trial)\b',
                r'\b(motion|order|petition|filing|case number)\b'
            ],
            'communication': [
                r'\b(text|message|call|phone|email|communication)\b',
                r'\b(received|sent|reply|response)\b'
            ]
        }
        
        # Duplicate detection
        self.processed_hashes = set()
        
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║         🔍 HARPER'S ENHANCED QUALITY PROCESSOR 🔍                ║
║                                                                  ║
║  ✨ Advanced OCR with Quality Control & Smart Categorization    ║
║  📊 Confidence Scoring & Duplicate Detection                    ║
║  🎯 Professional Legal Documentation System                     ║
║                                                                  ║
║  📋 Case: FDSJ-739-24                                          ║
║  🗂️ Processing: Multi-format Evidence Files                    ║
║  💎 Output: High-Quality Structured Data                       ║
╚══════════════════════════════════════════════════════════════════╝
        """)

    def setup_directories(self):
        """Setup all required directories."""
        self.base_dir = Path("custody_screenshots_smart_renamed")
        self.output_dir = Path("output")
        self.quality_dir = Path("quality_reports")
        self.backup_dir = Path("secure_backups")
        
        for directory in [self.output_dir, self.quality_dir, self.backup_dir]:
            directory.mkdir(exist_ok=True)
        
        # Generate unique output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_filename = self.output_dir / f"harper_enhanced_results_{timestamp}.csv"
        self.quality_report = self.quality_dir / f"quality_report_{timestamp}.json"

    def setup_logging(self):
        """Setup comprehensive logging system."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"enhanced_processor_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def calculate_image_hash(self, image_path: Path) -> str:
        """Calculate hash for duplicate detection."""
        try:
            with open(image_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return None

    def advanced_image_preprocessing(self, image_path: Path) -> List[Image.Image]:
        """Advanced image preprocessing with multiple enhancement techniques."""
        enhanced_images = []
        
        try:
            # Load original image
            original = Image.open(image_path)
            if original.mode != 'RGB':
                original = original.convert('RGB')
            
            # Method 1: Standard enhancement
            image1 = original.copy()
            enhancer = ImageEnhance.Contrast(image1)
            image1 = enhancer.enhance(1.5)
            enhancer = ImageEnhance.Sharpness(image1)
            image1 = enhancer.enhance(2.0)
            enhanced_images.append(('standard', image1.convert('L')))
            
            # Method 2: High contrast for screenshots
            image2 = original.copy()
            enhancer = ImageEnhance.Contrast(image2)
            image2 = enhancer.enhance(2.0)
            image2 = image2.convert('L')
            enhanced_images.append(('high_contrast', image2))
            
            # Method 3: OpenCV-based preprocessing for difficult images
            try:
                # Convert PIL to OpenCV
                cv_image = cv2.cvtColor(np.array(original), cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
                
                # Adaptive thresholding
                adaptive = cv2.adaptiveThreshold(
                    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
                )
                
                # Convert back to PIL
                image3 = Image.fromarray(adaptive)
                enhanced_images.append(('adaptive', image3))
                
            except Exception as e:
                self.logger.debug(f"OpenCV preprocessing failed for {image_path}: {e}")
            
            return enhanced_images
            
        except Exception as e:
            self.logger.error(f"Image preprocessing failed for {image_path}: {e}")
            return []

    def extract_text_with_confidence(self, image: Image.Image, config: str = 'standard') -> Tuple[str, float, Dict]:
        """Extract text with confidence scoring and detailed analysis."""
        try:
            # Get OCR data with confidence
            ocr_config = self.ocr_configs.get(config, self.ocr_configs['standard'])
            data = pytesseract.image_to_data(image, config=ocr_config, output_type=pytesseract.Output.DICT)
            
            # Extract text and calculate confidence
            words = []
            confidences = []
            
            for i, word in enumerate(data['text']):
                if word.strip():
                    words.append(word)
                    confidences.append(float(data['conf'][i]))
            
            text = ' '.join(words)
            avg_confidence = statistics.mean(confidences) if confidences else 0.0
            
            # Additional analysis
            analysis = {
                'word_count': len(words),
                'char_count': len(text),
                'avg_confidence': avg_confidence,
                'min_confidence': min(confidences) if confidences else 0.0,
                'max_confidence': max(confidences) if confidences else 0.0,
                'low_confidence_words': sum(1 for c in confidences if c < 60),
                'has_suspicious_patterns': any(re.search(pattern, text, re.IGNORECASE) for pattern in self.suspicious_patterns)
            }
            
            return text, avg_confidence, analysis
            
        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
            return "", 0.0, {}

    def categorize_content(self, text: str, filename: str) -> List[str]:
        """Smart content categorization based on text analysis."""
        categories = []
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        # Check filename-based categories first
        for category, patterns in self.category_patterns.items():
            if any(keyword in filename_lower for keyword in category.split('_')):
                categories.append(category)
                continue
            
            # Check text content patterns
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    categories.append(category)
                    break
        
        # Default category if none found
        if not categories:
            categories.append('general')
        
        return categories

    def assess_quality(self, text: str, confidence: float, analysis: Dict) -> Tuple[str, int]:
        """Assess the quality of extracted text and assign quality score."""
        score = 0
        issues = []
        
        # Confidence scoring (40 points)
        if confidence >= 85:
            score += 40
        elif confidence >= 70:
            score += 30
        elif confidence >= 50:
            score += 20
        else:
            score += 10
            issues.append(f"Low confidence: {confidence:.1f}%")
        
        # Text length and content (30 points)
        if analysis.get('char_count', 0) >= 100:
            score += 30
        elif analysis.get('char_count', 0) >= 50:
            score += 20
        elif analysis.get('char_count', 0) >= 20:
            score += 10
        else:
            issues.append(f"Short text: {analysis.get('char_count', 0)} characters")
        
        # Word quality (20 points)
        if analysis.get('low_confidence_words', 0) == 0:
            score += 20
        elif analysis.get('low_confidence_words', 0) <= 2:
            score += 15
        elif analysis.get('low_confidence_words', 0) <= 5:
            score += 10
        else:
            issues.append(f"Many low-confidence words: {analysis.get('low_confidence_words', 0)}")
        
        # Pattern analysis (10 points)
        if not analysis.get('has_suspicious_patterns', False):
            score += 10
        else:
            issues.append("Contains suspicious patterns")
        
        # Determine quality level
        if score >= 85:
            quality = "HIGH"
        elif score >= 60:
            quality = "MEDIUM"
        else:
            quality = "LOW"
        
        return quality, score

    def process_single_file(self, file_path: Path) -> Optional[Dict]:
        """Process a single evidence file with comprehensive analysis."""
        try:
            # Check for duplicates
            file_hash = self.calculate_image_hash(file_path)
            if file_hash and file_hash in self.processed_hashes:
                self.stats['duplicates'] += 1
                self.logger.info(f"⚠️ Duplicate detected: {file_path.name}")
                return None
            
            if file_hash:
                self.processed_hashes.add(file_hash)
            
            # Get enhanced images
            enhanced_images = self.advanced_image_preprocessing(file_path)
            if not enhanced_images:
                self.stats['failed'] += 1
                return None
            
            # Try different enhancement methods and keep best result
            best_result = None
            best_confidence = 0.0
            
            for method_name, enhanced_image in enhanced_images:
                text, confidence, analysis = self.extract_text_with_confidence(enhanced_image)
                
                if confidence > best_confidence and len(text.strip()) > self.min_text_length:
                    best_confidence = confidence
                    best_result = {
                        'text': text,
                        'confidence': confidence,
                        'analysis': analysis,
                        'method': method_name
                    }
            
            if not best_result or best_confidence < self.min_confidence:
                self.stats['failed'] += 1
                self.logger.warning(f"❌ Low quality result for {file_path.name}: {best_confidence:.1f}%")
                return None
            
            # Categorize content
            categories = self.categorize_content(best_result['text'], file_path.name)
            
            # Assess quality
            quality, quality_score = self.assess_quality(
                best_result['text'], 
                best_result['confidence'], 
                best_result['analysis']
            )
            
            # Update statistics
            self.stats['total_processed'] += 1
            if quality == "HIGH":
                self.stats['high_quality'] += 1
            elif quality == "MEDIUM":
                self.stats['medium_quality'] += 1
            else:
                self.stats['low_quality'] += 1
            
            for category in categories:
                self.stats['categories'][category] = self.stats['categories'].get(category, 0) + 1
            
            # Create comprehensive result
            result = {
                'filename': file_path.name,
                'filepath': str(file_path),
                'text_content': best_result['text'],
                'confidence_score': best_result['confidence'],
                'quality_level': quality,
                'quality_score': quality_score,
                'categories': ', '.join(categories),
                'word_count': best_result['analysis'].get('word_count', 0),
                'character_count': best_result['analysis'].get('char_count', 0),
                'processing_method': best_result['method'],
                'file_hash': file_hash,
                'processed_timestamp': datetime.now().isoformat(),
                'file_size': file_path.stat().st_size,
                'file_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            
            # Log successful processing
            status_icon = "🟢" if quality == "HIGH" else "🟡" if quality == "MEDIUM" else "🔴"
            self.logger.info(f"{status_icon} {file_path.name} | {quality} | {best_result['confidence']:.1f}% | {categories[0]}")
            
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            self.logger.error(f"❌ Processing failed for {file_path}: {e}")
            return None

    def process_all_evidence(self):
        """Process all evidence files with progress tracking."""
        print("\n🔍 SCANNING FOR EVIDENCE FILES...")
        
        # Find all image files
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
        all_files = []
        
        for ext in image_extensions:
            all_files.extend(self.base_dir.rglob(f"*{ext}"))
            all_files.extend(self.base_dir.rglob(f"*{ext.upper()}"))
        
        print(f"📁 Found {len(all_files)} image files to process")
        
        if not all_files:
            print("⚠️ No image files found for processing")
            return
        
        # Process files with progress bar
        results = []
        with tqdm(total=len(all_files), desc="Processing Evidence", unit="files") as pbar:
            for file_path in all_files:
                pbar.set_description(f"Processing {file_path.name[:30]}...")
                
                result = self.process_single_file(file_path)
                if result:
                    results.append(result)
                
                pbar.update(1)
                
                # Update progress display
                pbar.set_postfix({
                    'Success': f"{len(results)}",
                    'Failed': f"{self.stats['failed']}",
                    'Quality': f"H:{self.stats['high_quality']} M:{self.stats['medium_quality']} L:{self.stats['low_quality']}"
                })
        
        # Save results
        self.save_results(results)
        self.generate_quality_report()
        
        print(f"\n✅ PROCESSING COMPLETE!")
        print(f"📊 Total Processed: {len(results)}")
        print(f"🎯 High Quality: {self.stats['high_quality']}")
        print(f"⚡ Medium Quality: {self.stats['medium_quality']}")
        print(f"🔧 Low Quality: {self.stats['low_quality']}")
        print(f"❌ Failed: {self.stats['failed']}")
        print(f"🔄 Duplicates: {self.stats['duplicates']}")
        print(f"💾 Results saved to: {self.csv_filename}")

    def save_results(self, results: List[Dict]):
        """Save processing results to CSV with comprehensive data."""
        if not results:
            print("⚠️ No results to save")
            return
        
        # Define CSV headers
        headers = [
            'filename', 'filepath', 'text_content', 'confidence_score', 
            'quality_level', 'quality_score', 'categories', 'word_count',
            'character_count', 'processing_method', 'file_hash',
            'processed_timestamp', 'file_size', 'file_modified'
        ]
        
        try:
            with open(ensure_long_path(self.csv_filename), 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(results)
            
            print(f"💾 Results saved to: {self.csv_filename}")
            
            # Create backup
            backup_filename = self.backup_dir / f"enhanced_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            import shutil
            shutil.copy2(ensure_long_path(self.csv_filename), ensure_long_path(backup_filename))
            print(f"🔒 Backup created: {backup_filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")

    def generate_quality_report(self):
        """Generate comprehensive quality report."""
        report = {
            'processing_summary': {
                'timestamp': datetime.now().isoformat(),
                'total_files_found': self.stats['total_processed'] + self.stats['failed'] + self.stats['duplicates'],
                'total_processed': self.stats['total_processed'],
                'failed_processing': self.stats['failed'],
                'duplicates_detected': self.stats['duplicates'],
                'success_rate': (self.stats['total_processed'] / (self.stats['total_processed'] + self.stats['failed']) * 100) if (self.stats['total_processed'] + self.stats['failed']) > 0 else 0
            },
            'quality_distribution': {
                'high_quality': self.stats['high_quality'],
                'medium_quality': self.stats['medium_quality'],
                'low_quality': self.stats['low_quality'],
                'high_quality_percentage': (self.stats['high_quality'] / self.stats['total_processed'] * 100) if self.stats['total_processed'] > 0 else 0
            },
            'category_distribution': self.stats['categories'],
            'recommendations': []
        }
        
        # Add recommendations based on results
        if report['quality_distribution']['high_quality_percentage'] < 60:
            report['recommendations'].append("Consider improving image quality or scanning resolution")
        
        if self.stats['failed'] > self.stats['total_processed'] * 0.2:
            report['recommendations'].append("High failure rate detected - check image formats and quality")
        
        if self.stats['duplicates'] > 10:
            report['recommendations'].append("Many duplicates detected - consider file organization")
        
        # Save quality report
        try:
            with open(ensure_long_path(self.quality_report), 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"📊 Quality report saved: {self.quality_report}")
            
        except Exception as e:
            self.logger.error(f"Failed to save quality report: {e}")

def main():
    """Main processing function."""
    try:
        processor = EnhancedQualityProcessor()
        processor.process_all_evidence()
        
    except KeyboardInterrupt:
        print("\n🛑 Processing interrupted by user")
    except Exception as e:
        print(f"❌ Critical error: {e}")
        logging.error(f"Critical error in main: {e}")

if __name__ == "__main__":
    main()