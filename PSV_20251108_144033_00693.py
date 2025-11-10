#!/usr/bin/env python3
"""
Intelligent OCR Processor
Tests multiple preprocessing methods and automatically selects the best results
Designed to fix shitty OCR from messaging app screenshots
"""

import pytesseract
import cv2
import os
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
from image_preprocessor import (
    preprocess_image_for_ocr, 
    preprocess_messaging_app_screenshot,
    preprocess_with_multiple_methods,
    cleanup_temp_files
)
from config.settings import tesseract_config, min_ocr_confidence

# Set Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntelligentOCRProcessor:
    """OCR processor that automatically selects the best preprocessing method"""
    
    def __init__(self):
        self.methods_tested = 0
        self.improvements_found = 0
        
    def test_multiple_preprocessing(self, image_path):
        """
        Test multiple preprocessing methods and return the best result
        """
        logger.info(f"Testing multiple methods for: {os.path.basename(image_path)}")
        
        # Get all preprocessing variations
        methods = preprocess_with_multiple_methods(image_path)
        
        best_result = None
        best_confidence = 0
        best_method = "original"
        
        for method_name, temp_path in methods:
            try:
                # Run OCR on this variation
                text = pytesseract.image_to_string(temp_path, config=tesseract_config)
                
                # Get confidence data
                data = pytesseract.image_to_data(
                    temp_path, 
                    config=tesseract_config, 
                    output_type=pytesseract.Output.DICT
                )
                
                # Calculate confidence
                confidences = [c for c, t in zip(data['conf'], data['text']) if t.strip() and c > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                logger.info(f"   {method_name}: {avg_confidence:.1f}% confidence, {len(text.strip())} chars")
                
                # Track the best result
                if avg_confidence > best_confidence:
                    best_confidence = avg_confidence
                    best_result = {
                        'text': text,
                        'confidence': avg_confidence,
                        'method': method_name,
                        'temp_path': temp_path
                    }
                    best_method = method_name
                
                # Clean up temp files (except the best one)
                if method_name != best_method and temp_path != image_path:
                    cleanup_temp_files(temp_path, image_path)
                    
            except Exception as e:
                logger.error(f"   {method_name} failed: {e}")
                # Clean up failed temp file
                if temp_path != image_path:
                    cleanup_temp_files(temp_path, image_path)
        
        # Clean up the best temp file too
        if best_result and best_result['temp_path'] != image_path:
            cleanup_temp_files(best_result['temp_path'], image_path)
        
        self.methods_tested += 1
        if best_confidence > 70:  # Good result threshold
            self.improvements_found += 1
        
        logger.info(f"   BEST: {best_method} with {best_confidence:.1f}% confidence")
        
        return best_result if best_result else {
            'text': '', 
            'confidence': 0, 
            'method': 'failed',
            'temp_path': image_path
        }
    
    def process_problematic_files(self, csv_file, max_files=100):
        """
        Identify and reprocess the most problematic files from existing OCR results
        """
        print(f"🔍 Identifying problematic files in {csv_file}")
        
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
            
            # Find problematic files (low confidence, short text, garbled)
            problem_files = []
            
            for idx, row in df.iterrows():
                filename = row.get('filename', '')
                filepath = row.get('filepath', '')
                raw_text = str(row.get('raw_text', ''))
                confidence = row.get('confidence', 100)
                
                # Criteria for reprocessing
                needs_reprocess = False
                issues = []
                
                if confidence < 50:
                    needs_reprocess = True
                    issues.append(f"Very low confidence ({confidence:.1f}%)")
                
                if len(raw_text.strip()) < 20:
                    needs_reprocess = True
                    issues.append("Very short text")
                
                # Check for garbled text (lots of single characters)
                words = raw_text.split()
                if len(words) > 3:
                    single_chars = [w for w in words if len(w) == 1 and w.isalpha()]
                    if len(single_chars) > len(words) * 0.4:  # >40% single chars
                        needs_reprocess = True
                        issues.append("Garbled (many single chars)")
                
                if needs_reprocess and filepath and os.path.exists(filepath):
                    problem_files.append({
                        'filename': filename,
                        'filepath': filepath,
                        'original_confidence': confidence,
                        'original_text': raw_text[:100],
                        'issues': "; ".join(issues)
                    })
                
                # Limit to avoid processing everything
                if len(problem_files) >= max_files:
                    break
            
            print(f"   Found {len(problem_files)} files needing intelligent reprocessing")
            
            if not problem_files:
                print("✅ No problematic files found!")
                return None
            
            # Process the problematic files
            print(f"🤖 Applying intelligent OCR to {len(problem_files)} files...")
            
            results = []
            for i, file_info in enumerate(problem_files, 1):
                print(f"\n[{i}/{len(problem_files)}] Processing: {file_info['filename']}")
                
                # Apply intelligent preprocessing
                best_result = self.test_multiple_preprocessing(file_info['filepath'])
                
                if best_result['confidence'] > file_info['original_confidence']:
                    improvement = best_result['confidence'] - file_info['original_confidence']
                    print(f"   ✅ IMPROVED: +{improvement:.1f}% confidence using {best_result['method']}")
                else:
                    print(f"   ❌ No improvement found")
                
                # Save result
                results.append({
                    'filename': file_info['filename'],
                    'filepath': file_info['filepath'],
                    'original_confidence': file_info['original_confidence'],
                    'new_confidence': best_result['confidence'],
                    'improvement': best_result['confidence'] - file_info['original_confidence'],
                    'best_method': best_result['method'],
                    'original_text': file_info['original_text'],
                    'new_text': best_result['text'][:100],
                    'issues_fixed': file_info['issues']
                })
            
            # Save results
            if results:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = f"output/intelligent_ocr_results_{timestamp}.csv"
                
                results_df = pd.DataFrame(results)
                results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
                
                # Report results
                improvements = results_df[results_df['improvement'] > 0]
                avg_improvement = improvements['improvement'].mean() if not improvements.empty else 0
                
                print(f"\n🎯 INTELLIGENT OCR COMPLETE!")
                print(f"   Files processed: {len(results)}")
                print(f"   Files improved: {len(improvements)} ({len(improvements)/len(results)*100:.1f}%)")
                print(f"   Average improvement: +{avg_improvement:.1f}% confidence")
                print(f"   Results saved to: {output_file}")
                
                # Show best improvements
                if not improvements.empty:
                    top_improvements = improvements.nlargest(5, 'improvement')
                    print(f"\n🏆 TOP IMPROVEMENTS:")
                    for _, row in top_improvements.iterrows():
                        print(f"   {row['filename']}: {row['original_confidence']:.1f}% → {row['new_confidence']:.1f}% (+{row['improvement']:.1f}%)")
                
                return output_file
            
        except Exception as e:
            logger.error(f"Intelligent processing failed: {e}")
            return None


def main():
    """Main execution"""
    processor = IntelligentOCRProcessor()
    
    print("🤖 Intelligent OCR Processor")
    print("=" * 50)
    print("Automatically tests multiple preprocessing methods")
    print("and selects the best results for shitty screenshots")
    print()
    
    # Find the most recent OCR results
    output_dir = Path("output")
    csv_files = list(output_dir.glob("enhanced_ocr_results_*.csv"))
    
    if not csv_files:
        print("❌ No enhanced OCR results found")
        print("   Run the enhanced OCR processor first")
        return
    
    # Use most recent file
    latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
    print(f"📁 Using OCR results: {latest_file.name}")
    
    # Ask how many files to process
    try:
        max_files = input("How many problematic files to reprocess? (default: 50): ").strip()
        max_files = int(max_files) if max_files else 50
    except:
        max_files = 50
    
    # Process the files
    result_file = processor.process_problematic_files(str(latest_file), max_files)
    
    if result_file:
        print(f"\n✅ Intelligent OCR completed!")
        print(f"📊 Check {result_file} for detailed results")
        print(f"🎯 Methods tested: {processor.methods_tested}")
        print(f"💪 Significant improvements: {processor.improvements_found}")
    else:
        print("\n❌ No files processed")


if __name__ == "__main__":
    main()