#!/usr/bin/env python3
"""
Smart Batch OCR Learning System
Processes evidence in small batches with learning feedback
"""

import pytesseract
from PIL import Image
import pandas as pd
import numpy as np
from pathlib import Path
import re
from datetime import datetime
import json
import cv2
from tqdm import tqdm
import logging
from utils.path_utils import ensure_long_path
import pickle
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class SmartBatchOCRLearner:
    """OCR processor with adaptive learning from corrections"""
    
    def __init__(self, batch_size=50):
        self.batch_size = batch_size
        self.learning_data = self.load_learning_data()
        self.current_batch = 0
        self.corrections_file = "output/ocr_corrections.json"
        self.learning_model_file = "output/ocr_learning_model.pkl"
        
        # OCR configuration that we can adapt
        self.ocr_configs = [
            r'--oem 3 --psm 6',  # Default uniform block
            r'--oem 3 --psm 4',  # Single column text
            r'--oem 3 --psm 8',  # Single word
            r'--oem 3 --psm 13', # Raw line
            r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:;!?@()-',
        ]
        self.current_config_index = 0
        
    def load_learning_data(self):
        """Load previous corrections and learning patterns"""
        try:
            if os.path.exists(self.corrections_file):
                with open(self.corrections_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load learning data: {e}")
        return {"corrections": {}, "patterns": {}, "config_performance": {}}
    
    def save_learning_data(self):
        """Save corrections and learning patterns"""
        try:
            os.makedirs("output", exist_ok=True)
            with open(self.corrections_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Could not save learning data: {e}")
    
    def preprocess_image_adaptive(self, image_path):
        """Adaptive preprocessing based on learning"""
        try:
            # Try OpenCV read first
            img = cv2.imread(str(image_path))
            if img is None:
                # Fallback: try PIL with Windows long-path support
                from PIL import Image as _PILImage
                pil_img = _PILImage.open(ensure_long_path(image_path))
                img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                
            # Multiple preprocessing approaches
            processed_variants = []
            
            # Variant 1: Standard grayscale + threshold
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            processed_variants.append(Image.fromarray(binary))
            
            # Variant 2: Denoised + enhanced contrast
            denoised = cv2.fastNlMeansDenoising(gray)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            processed_variants.append(Image.fromarray(enhanced))
            
            # Variant 3: Morphological operations (for text cleanup)
            kernel = np.ones((1,1), np.uint8)
            morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            processed_variants.append(Image.fromarray(morph))
            
            return processed_variants
            
        except Exception as e:
            logger.error(f"Error preprocessing {image_path}: {e}")
            return []
    
    def extract_text_with_confidence(self, image, config):
        """Extract text with confidence scoring"""
        try:
            # Get detailed data with confidence scores
            data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
            
            # Filter by confidence and reconstruct text
            confident_words = []
            confidence_scores = []
            
            for i in range(len(data['text'])):
                conf = int(data['conf'][i])
                text = data['text'][i].strip()
                
                if conf > 30 and text:  # Confidence threshold
                    confident_words.append(text)
                    confidence_scores.append(conf)
            
            if confident_words:
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
                text = ' '.join(confident_words)
                return text, avg_confidence
            else:
                return "", 0
                
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return "", 0
    
    def detect_sender_recipient_smart(self, text, filename):
        """Smart sender/recipient detection with Craig's rules"""
        sender = "Craig"  # Default
        recipient = "Unknown"
        
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        # Extract first few lines for header analysis
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        header_text = ' '.join(lines[:5]).lower() if lines else ""
        
        # Craig's rules
        if any(phrase in header_text for phrase in ['my girl', 'emma']):
            recipient = "Emma"
        elif any(name in header_text for name in ['jane', 'ryan', 'matt', 'nick', 'kerrie']):
            for name in ['jane', 'ryan', 'matt', 'nick', 'kerrie']:
                if name in header_text:
                    recipient = name.title()
                    break
        elif any(name in header_text for name in ['cole', 'brooks', 'tony', 'baker']):
            if 'cole' in header_text or 'brooks' in header_text:
                sender = "Cole Brooks"
                recipient = "Emma"
            elif 'tony' in header_text or 'baker' in header_text:
                sender = "Tony Baker"
                recipient = "Emma"
        
        # Filename fallbacks
        if recipient == "Unknown":
            if 'emma' in filename_lower:
                recipient = "Emma"
            elif 'jane' in filename_lower:
                recipient = "Jane"
        
        return sender, recipient
    
    def process_batch(self, image_paths, batch_num):
        """Process a single batch of images"""
        logger.info(f"Processing batch {batch_num}: {len(image_paths)} images")
        
        batch_results = []
        batch_performance = {}
        
        for img_path in tqdm(image_paths, desc=f"Batch {batch_num}"):
            try:
                # Get multiple processed variants
                processed_images = self.preprocess_image_adaptive(img_path)
                
                if not processed_images:
                    continue
                
                # Try different OCR configs and pick best result
                best_text = ""
                best_confidence = 0
                best_config = self.ocr_configs[self.current_config_index]
                
                for config in self.ocr_configs:
                    for proc_img in processed_images:
                        text, confidence = self.extract_text_with_confidence(proc_img, config)
                        
                        if confidence > best_confidence:
                            best_text = text
                            best_confidence = confidence
                            best_config = config
                
                # Detect sender/recipient
                sender, recipient = self.detect_sender_recipient_smart(best_text, img_path.name)
                
                # Store result
                result = {
                    'filename': img_path.name,
                    'filepath': str(img_path),
                    'sender': sender,
                    'recipient': recipient,
                    'raw_text': best_text,
                    'formatted_text': best_text,  # Can be corrected later
                    'confidence': best_confidence,
                    'ocr_config': best_config,
                    'char_count': len(best_text),
                    'has_sender': sender != "Unknown",
                    'has_recipient': recipient != "Unknown",
                    'processed_date': datetime.now().isoformat(),
                    'batch_num': batch_num
                }
                batch_results.append(result)
                
                # Track config performance
                if best_config not in batch_performance:
                    batch_performance[best_config] = []
                batch_performance[best_config].append(best_confidence)
                
            except Exception as e:
                logger.error(f"Error processing {img_path}: {e}")
        
        # Update learning data with batch performance
        for config, confidences in batch_performance.items():
            avg_conf = sum(confidences) / len(confidences) if confidences else 0
            if config not in self.learning_data["config_performance"]:
                self.learning_data["config_performance"][config] = []
            self.learning_data["config_performance"][config].append(avg_conf)
        
        return batch_results
    
    def save_batch_results(self, results, batch_num):
        """Save batch results to CSV"""
        if not results:
            return None
            
        df = pd.DataFrame(results)
        output_file = f"output/batch_{batch_num:03d}_ocr_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            df.to_csv(ensure_long_path(output_file), index=False, encoding='utf-8')
            logger.info(f"Batch {batch_num} saved: {output_file} ({len(results)} results)")
            return output_file
        except Exception as e:
            logger.error(f"Error saving batch {batch_num}: {e}")
            return None
    
    def process_in_batches(self, input_dir="custody_screenshots"):
        """Process all images in manageable batches"""
        input_path = Path(input_dir)
        
        # Get all image files
        image_extensions = {'.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.heic'}
        all_images = []
        
        for ext in image_extensions:
            all_images.extend(list(input_path.glob(f"**/*{ext}")))
            all_images.extend(list(input_path.glob(f"**/*{ext.upper()}")))
        
        logger.info(f"Found {len(all_images)} images to process in batches of {self.batch_size}")
        
        # Process in batches
        batch_files = []
        for i in range(0, len(all_images), self.batch_size):
            batch_num = i // self.batch_size + 1
            batch_images = all_images[i:i + self.batch_size]
            
            # Process batch
            results = self.process_batch(batch_images, batch_num)
            
            # Save batch
            batch_file = self.save_batch_results(results, batch_num)
            if batch_file:
                batch_files.append(batch_file)
            
            # Save learning progress
            self.save_learning_data()
            
            # User can review and correct this batch before continuing
            print(f"\n🎯 Batch {batch_num} complete!")
            print(f"   Results: {batch_file}")
            print(f"   Processed: {len(results)} images")
            
            # Ask if user wants to continue or review
            response = input(f"\nContinue to next batch? (y/n/review): ").lower()
            if response == 'n':
                logger.info("Stopping at user request")
                break
            elif response == 'review':
                logger.info(f"Please review {batch_file} and make corrections")
                input("Press Enter when ready to continue...")
        
        logger.info(f"Batch processing complete! Created {len(batch_files)} batch files")
        return batch_files


def main():
    """Main entry point"""
    processor = SmartBatchOCRLearner(batch_size=50)  # Start with 50 images per batch
    
    logger.info("Starting smart batch OCR learning system...")
    logger.info(f"Batch size: {processor.batch_size}")
    
    batch_files = processor.process_in_batches()
    
    if batch_files:
        logger.info("\n=== Batch Processing Summary ===")
        for i, file in enumerate(batch_files, 1):
            logger.info(f"Batch {i}: {file}")
        
        # Option to merge all batches
        merge = input("\nMerge all batches into single file? (y/n): ").lower()
        if merge == 'y':
            # Merge all batch CSVs
            all_dfs = []
            for file in batch_files:
                try:
                    df = pd.read_csv(file, encoding='utf-8')
                    all_dfs.append(df)
                except Exception as e:
                    logger.error(f"Error reading {file}: {e}")
            
            if all_dfs:
                merged_df = pd.concat(all_dfs, ignore_index=True)
                merged_file = f"output/merged_smart_ocr_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                merged_df.to_csv(merged_file, index=False, encoding='utf-8')
                logger.info(f"Merged results saved to: {merged_file}")


if __name__ == "__main__":
    main()