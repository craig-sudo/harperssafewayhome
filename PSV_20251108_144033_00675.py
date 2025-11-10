#!/usr/bin/env python3
"""
Enhanced OCR Processor - Round 3 with Advanced Preprocessing
Extracts sender/recipient and properly formatted text from screenshots
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
from image_preprocessor import preprocess_image_for_ocr, cleanup_temp_files
from config.settings import min_ocr_confidence, tesseract_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class EnhancedOCRProcessor:
    """Smart OCR that extracts sender/recipient and formats text properly"""
    
    def __init__(self):
        self.sender_keywords = [
            'You', 'Me', 'Dale', 'harper', 'harpers', 
            # Add more known senders
        ]
        self.recipient_keywords = [
            'Emma', 'Jane', 'Mom', 'Dad', 'Nanny',
            # Add more known recipients
        ]
        
        # Common messaging app indicators
        self.app_indicators = {
            'text': ['iMessage', 'Messages', 'SMS'],
            'whatsapp': ['WhatsApp'],
            'facebook': ['Messenger', 'Facebook'],
            'email': ['Gmail', 'Outlook', 'Mail', '@']
        }
        
    def preprocess_image(self, image_path):
        """Enhanced preprocessing for better OCR"""
        # Try OpenCV read first
        img = cv2.imread(str(image_path))
        if img is None:
            # Fallback: try PIL with Windows long-path support
            try:
                from PIL import Image as _PILImage
                pil_img = _PILImage.open(ensure_long_path(image_path))
                img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            except Exception:
                return None
            
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Adaptive threshold for better text extraction
        binary = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(binary)
        
        return Image.fromarray(enhanced)
    
    def extract_text_with_layout(self, image):
        """Extract text preserving layout and spacing"""
        # Use enhanced Tesseract configuration
        
        # Get detailed data with coordinates
        data = pytesseract.image_to_data(image, config=tesseract_config, output_type=pytesseract.Output.DICT)
        
        # Reconstruct text with proper spacing
        lines = {}
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 30:  # Confidence threshold
                text = data['text'][i].strip()
                if text:
                    line_num = data['line_num'][i]
                    block_num = data['block_num'][i]
                    
                    key = (block_num, line_num)
                    if key not in lines:
                        lines[key] = []
                    lines[key].append({
                        'text': text,
                        'left': data['left'][i],
                        'top': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    })
        
        # Sort and format lines
        formatted_lines = []
        for key in sorted(lines.keys()):
            # Sort words in line by left position
            words = sorted(lines[key], key=lambda x: x['left'])
            line_text = ' '.join([w['text'] for w in words])
            formatted_lines.append(line_text)
        
        return '\n'.join(formatted_lines)
    
    def detect_sender_recipient(self, text, filename):
        """
        Detect sender and recipient using Craig's specific rules:
        - "My Girl" or "Emma" at top → Craig (right) & Emma (left)
        - "Jane", "Ryan", "Matt", "Nick", "Kerrie" → Craig (right) & them (left)
        - "Cole Brooks", "Tony Baker" → them (left) & Emma (right)
        """
        sender = "Unknown"
        recipient = "Unknown"
        
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        # Extract first few lines for header analysis (contact name usually at top)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        header_text = ' '.join(lines[:5]).lower() if lines else ""
        
        # RULE 1: "My Girl" or "Emma" at top → Craig & Emma conversation
        if any(phrase in header_text for phrase in ['my girl', 'emma']):
            sender = "Craig"
            recipient = "Emma"
            return sender, recipient
        
        # RULE 2: Jane, Ryan, Matt, Nick, Kerrie → Craig & them
        contact_map = {
            'jane': 'Jane',
            'ryan': 'Ryan',
            'matt': 'Matt',
            'nick': 'Nick',
            'kerrie': 'Kerrie'
        }
        
        for key, name in contact_map.items():
            if key in header_text or key in filename_lower:
                sender = "Craig"
                recipient = name
                return sender, recipient
        
        # RULE 3: Cole Brooks or Tony Baker → them & Emma
        if 'cole' in header_text or 'brooks' in header_text or 'cole' in filename_lower:
            sender = "Cole Brooks"
            recipient = "Emma"
            return sender, recipient
            
        if 'tony' in header_text or 'baker' in header_text or 'tony' in filename_lower:
            sender = "Tony Baker"
            recipient = "Emma"
            return sender, recipient
        
        # Fallback: Check filename for common patterns
        if 'emma' in filename_lower:
            sender = "Craig"
            recipient = "Emma"
        elif 'jane' in filename_lower or 'nanny' in filename_lower:
            sender = "Craig"
            recipient = "Jane"
        elif 'mom' in filename_lower or 'mother' in filename_lower:
            sender = "Craig"
            recipient = "Mom"
        
        # Email detection for non-text messages
        email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        emails = re.findall(email_pattern, text)
        
        if emails and sender == "Unknown":
            # First email is usually sender or recipient
            if len(emails) >= 2:
                sender = emails[0]
                recipient = emails[1]
            elif len(emails) == 1:
                # Check context
                email = emails[0]
                idx = text.lower().find(email.lower())
                before = text[:idx].lower()[-50:] if idx > 0 else ""
                
                if any(word in before for word in ['from:', 'sender:', 'de:']):
                    sender = email
                    recipient = "Unknown"
                elif any(word in before for word in ['to:', 'para:', 'recipient:']):
                    sender = "Craig"
                    recipient = email
        
        # Default to Craig as sender (his screenshots)
        if sender == "Unknown":
            sender = "Craig"
        
        return sender, recipient
    
    def format_message_text(self, text):
        """Clean and format message text for readability"""
        # Remove UI elements and timestamps from body
        lines = text.split('\n')
        clean_lines = []
        
        skip_patterns = [
            r'^\d{1,2}:\d{2}',  # Time
            r'^\d{1,2}/\d{1,2}/\d{2,4}',  # Date
            r'^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)',  # Day
            r'^(iMessage|WhatsApp|Messenger|Messages)',  # App names
            r'^(Delivered|Read|Sent|Typing)',  # Status
            r'^\s*$',  # Empty lines
            r'^[\W_]{3,}$',  # Lines with only symbols
            r'^[A-Z]{1}\s*$',  # Single capital letters alone
        ]
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 2:
                continue
                
            skip = False
            for pattern in skip_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    skip = True
                    break
            
            if not skip:
                # Clean up common OCR errors
                line = re.sub(r'[|!]{2,}', ' ', line)  # Multiple pipes/exclamations
                line = re.sub(r'\s{2,}', ' ', line)  # Multiple spaces
                line = line.strip()
                
                if len(line) > 2:  # Avoid very short fragments
                    clean_lines.append(line)
        
        # Join with proper spacing
        formatted = '\n'.join(clean_lines)
        
        # Final cleanup
        formatted = re.sub(r'\n{3,}', '\n\n', formatted)  # Too many newlines
        
        return formatted.strip()
    
    def process_image(self, image_path):
        """Process single image and extract all info with enhanced preprocessing"""
        temp_path = None
        
        try:
            # NEW: Advanced preprocessing for better OCR
            temp_path = preprocess_image_for_ocr(image_path)
            
            # Load the preprocessed image
            processed_img = Image.open(temp_path)
            
            # Extract text using enhanced Tesseract config
            raw_text = pytesseract.image_to_string(processed_img, config=tesseract_config)
            
            # NEW: Get confidence data for quality control
            data = pytesseract.image_to_data(processed_img, config=tesseract_config, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence of text lines
            confidences = [c for c, t in zip(data['conf'], data['text']) if t.strip() and c > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Also get layout-aware text as backup
            layout_text = self.extract_text_with_layout(processed_img)
            
            # Use whichever is longer/better
            text = layout_text if len(layout_text) > len(raw_text) else raw_text
            
            if not text.strip():
                return None
            
            # Detect sender/recipient
            filename = Path(image_path).name
            sender, recipient = self.detect_sender_recipient(text, filename)
            
            # Format message text
            formatted_text = self.format_message_text(text)
            
            # NEW: Determine processing status based on confidence
            status = "SUCCESS"
            if avg_confidence < min_ocr_confidence:
                status = "LOW_CONFIDENCE_FLAG"
                logger.warning(f"Low confidence ({avg_confidence:.1f}%) for {filename}")
            
            result = {
                'filename': filename,
                'filepath': str(image_path),
                'sender': sender,
                'recipient': recipient,
                'raw_text': text,
                'formatted_text': formatted_text,
                'confidence': round(avg_confidence, 2),
                'processing_status': status,
                'char_count': len(formatted_text),
                'has_sender': sender != "Unknown",
                'has_recipient': recipient != "Unknown"
            }
            
            # Clean up temporary file
            cleanup_temp_files(temp_path, image_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing {image_path}: {e}")
            
            # Clean up temporary file on error
            if temp_path:
                cleanup_temp_files(temp_path, image_path)
            
            return None
    
    def process_directory(self, input_dir, output_csv):
        """Process all images in directory"""
        input_path = Path(input_dir)
        
        # Find all images
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
        image_files = []
        for ext in image_extensions:
            image_files.extend(input_path.rglob(f'*{ext}'))
        
        logger.info(f"Found {len(image_files)} images to process")
        
        results = []
        for img_path in tqdm(image_files, desc="Processing images"):
            result = self.process_image(img_path)
            if result:
                results.append(result)
        
        # Create DataFrame
        df = pd.DataFrame(results)
        
        # Add metadata
        df['processed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df['ocr_version'] = '2.0_enhanced'
        
        # Save
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        logger.info(f"Saved {len(df)} results to {output_csv}")
        
        # Print statistics
        logger.info(f"\n=== Processing Statistics ===")
        logger.info(f"Total processed: {len(df)}")
        logger.info(f"With sender: {df['has_sender'].sum()}")
        logger.info(f"With recipient: {df['has_recipient'].sum()}")
        logger.info(f"Average text length: {df['char_count'].mean():.0f} chars")
        logger.info(f"Average OCR confidence: {df['confidence'].mean():.1f}%")
        
        # Quality control statistics
        low_confidence_count = df[df['processing_status'] == 'LOW_CONFIDENCE_FLAG'].shape[0]
        logger.info(f"Low confidence extractions: {low_confidence_count} ({low_confidence_count/len(df)*100:.1f}%)")
        
        if low_confidence_count > 0:
            logger.warning(f"⚠️  {low_confidence_count} files flagged for review due to low OCR confidence")
            logger.warning(f"   Consider manual review of files with confidence < {min_ocr_confidence}%")
        
        return df


def main():
    """Main execution"""
    processor = EnhancedOCRProcessor()
    
    # Input directory
    input_dir = Path('custody_screenshots')
    output_csv = Path('output') / f'enhanced_ocr_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    output_csv.parent.mkdir(exist_ok=True)
    
    # Process
    logger.info("Starting enhanced OCR processing...")
    df = processor.process_directory(input_dir, output_csv)
    
    logger.info(f"\n✅ Complete! Results saved to: {output_csv}")
    logger.info(f"You can now review and edit sender/recipient columns as needed.")
    
    # Create a sample preview file
    preview_file = output_csv.parent / f'preview_{output_csv.stem}.txt'
    with open(preview_file, 'w', encoding='utf-8') as f:
        f.write("=== SAMPLE EXTRACTIONS ===\n\n")
        for idx, row in df.head(10).iterrows():
            f.write(f"--- File: {row['filename']} ---\n")
            f.write(f"Sender: {row['sender']}\n")
            f.write(f"Recipient: {row['recipient']}\n")
            f.write(f"Formatted Text:\n{row['formatted_text']}\n")
            f.write("\n" + "="*80 + "\n\n")
    
    logger.info(f"Preview saved to: {preview_file}")


if __name__ == '__main__':
    main()
