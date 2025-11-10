#!/usr/bin/env python3
"""
OCR Test Tool - Test military-grade preprocessing on a single file
Quick verification that our advanced image processing works
"""

import os
import pytesseract
from pathlib import Path
import cv2
import numpy as np
from image_preprocessor import preprocess_image_for_ocr, preprocess_messaging_app_screenshot

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def test_single_file_ocr(image_path):
    """Test OCR on a single file with different preprocessing methods"""
    
    print(f"🔍 Testing OCR on: {os.path.basename(image_path)}")
    print("=" * 50)
    
    if not os.path.exists(image_path):
        print(f"❌ File not found: {image_path}")
        return
    
    try:
        # Test 1: Original (no preprocessing)
        print("1. ORIGINAL (no preprocessing):")
        text_original = pytesseract.image_to_string(image_path, config="--oem 3 --psm 6 -l eng --dpi 300")
        print(f"   Text: {text_original[:100]}...")
        print(f"   Length: {len(text_original)} chars")
        
        # Get confidence for original
        data_original = pytesseract.image_to_data(image_path, output_type=pytesseract.Output.DICT, config="--oem 3 --psm 6 -l eng --dpi 300")
        confidences_original = [c for c, t in zip(data_original['conf'], data_original['text']) if t.strip() and c > 0]
        avg_conf_original = sum(confidences_original) / len(confidences_original) if confidences_original else 0
        print(f"   Confidence: {avg_conf_original:.1f}%")
        print()
        
        # Test 2: Military-grade preprocessing
        print("2. MILITARY-GRADE PREPROCESSING:")
        temp_path_military = preprocess_image_for_ocr(image_path)
        
        if temp_path_military != image_path:
            text_military = pytesseract.image_to_string(temp_path_military, config="--oem 3 --psm 6 -l eng --dpi 300")
            print(f"   Text: {text_military[:100]}...")
            print(f"   Length: {len(text_military)} chars")
            
            # Get confidence for military
            data_military = pytesseract.image_to_data(temp_path_military, output_type=pytesseract.Output.DICT, config="--oem 3 --psm 6 -l eng --dpi 300")
            confidences_military = [c for c, t in zip(data_military['conf'], data_military['text']) if t.strip() and c > 0]
            avg_conf_military = sum(confidences_military) / len(confidences_military) if confidences_military else 0
            print(f"   Confidence: {avg_conf_military:.1f}%")
            print(f"   Improvement: {avg_conf_military - avg_conf_original:+.1f}%")
            
            # Clean up
            if os.path.exists(temp_path_military):
                os.remove(temp_path_military)
        else:
            print("   ❌ Preprocessing failed")
        print()
        
        # Test 3: Messaging app specialized
        print("3. MESSAGING APP SPECIALIZED:")
        temp_path_messaging = preprocess_messaging_app_screenshot(image_path)
        
        if temp_path_messaging != image_path:
            text_messaging = pytesseract.image_to_string(temp_path_messaging, config="--oem 3 --psm 6 -l eng --dpi 300")
            print(f"   Text: {text_messaging[:100]}...")
            print(f"   Length: {len(text_messaging)} chars")
            
            # Get confidence for messaging
            data_messaging = pytesseract.image_to_data(temp_path_messaging, output_type=pytesseract.Output.DICT, config="--oem 3 --psm 6 -l eng --dpi 300")
            confidences_messaging = [c for c, t in zip(data_messaging['conf'], data_messaging['text']) if t.strip() and c > 0]
            avg_conf_messaging = sum(confidences_messaging) / len(confidences_messaging) if confidences_messaging else 0
            print(f"   Confidence: {avg_conf_messaging:.1f}%")
            print(f"   Improvement: {avg_conf_messaging - avg_conf_original:+.1f}%")
            
            # Clean up
            if os.path.exists(temp_path_messaging):
                os.remove(temp_path_messaging)
        else:
            print("   ❌ Preprocessing failed")
        print()
        
        # Test 4: Extreme enhancement for really bad images
        print("4. EXTREME ENHANCEMENT:")
        img = cv2.imread(image_path)
        if img is not None:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Extreme contrast and denoising
            enhanced = cv2.convertScaleAbs(gray, alpha=3.0, beta=60)
            denoised = cv2.bilateralFilter(enhanced, 25, 100, 100)
            
            # Extreme Otsu with large morphology
            _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            kernel = np.ones((7, 7), np.uint8)
            extreme = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            temp_path_extreme = f"temp_extreme_{os.path.basename(image_path)}"
            cv2.imwrite(temp_path_extreme, extreme)
            
            text_extreme = pytesseract.image_to_string(temp_path_extreme, config="--oem 3 --psm 6 -l eng --dpi 300")
            print(f"   Text: {text_extreme[:100]}...")
            print(f"   Length: {len(text_extreme)} chars")
            
            # Get confidence for extreme
            data_extreme = pytesseract.image_to_data(temp_path_extreme, output_type=pytesseract.Output.DICT, config="--oem 3 --psm 6 -l eng --dpi 300")
            confidences_extreme = [c for c, t in zip(data_extreme['conf'], data_extreme['text']) if t.strip() and c > 0]
            avg_conf_extreme = sum(confidences_extreme) / len(confidences_extreme) if confidences_extreme else 0
            print(f"   Confidence: {avg_conf_extreme:.1f}%")
            print(f"   Improvement: {avg_conf_extreme - avg_conf_original:+.1f}%")
            
            # Clean up
            if os.path.exists(temp_path_extreme):
                os.remove(temp_path_extreme)
        print()
        
        print("🎯 TEST COMPLETE!")
        print(f"Best confidence: {max(avg_conf_original, avg_conf_military if 'avg_conf_military' in locals() else 0, avg_conf_messaging if 'avg_conf_messaging' in locals() else 0, avg_conf_extreme if 'avg_conf_extreme' in locals() else 0):.1f}%")
        
    except Exception as e:
        print(f"❌ OCR test failed: {e}")


def main():
    """Interactive test tool"""
    print("🔧 OCR Test Tool - Military-Grade Preprocessing")
    print("=" * 50)
    
    # Find some test images
    custody_dir = Path("custody_screenshots")
    if custody_dir.exists():
        image_files = []
        for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            image_files.extend(list(custody_dir.rglob(f'*{ext}')))
            image_files.extend(list(custody_dir.rglob(f'*{ext.upper()}')))
        
        if image_files:
            print(f"Found {len(image_files)} images. Testing a sample...")
            # Test the first few files
            for i, image_file in enumerate(image_files[:3]):
                print(f"\n{'='*60}")
                print(f"TEST {i+1}: {image_file.name}")
                print('='*60)
                test_single_file_ocr(str(image_file))
        else:
            print("❌ No images found in custody_screenshots")
    else:
        print("❌ custody_screenshots directory not found")
        print("Please specify a file manually:")
        file_path = input("Enter image path: ").strip('"')
        if os.path.exists(file_path):
            test_single_file_ocr(file_path)
        else:
            print("❌ File not found")


if __name__ == "__main__":
    main()