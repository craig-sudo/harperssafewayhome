#!/usr/bin/env python3
"""
OCR Quality Assessment Tool
Analyzes OCR results to identify low-quality extractions that need review
"""

import pandas as pd
import os
from pathlib import Path
import re

def analyze_ocr_quality(csv_file):
    """
    Analyze OCR results for quality indicators
    """
    print(f"📊 Analyzing OCR Quality: {csv_file}")
    print("=" * 60)
    
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
        
        # Basic statistics
        total_records = len(df)
        print(f"Total Records: {total_records}")
        
        if 'confidence' in df.columns:
            avg_confidence = df['confidence'].mean()
            min_confidence = df['confidence'].min()
            max_confidence = df['confidence'].max()
            
            print(f"Average Confidence: {avg_confidence:.1f}%")
            print(f"Confidence Range: {min_confidence:.1f}% - {max_confidence:.1f}%")
            
            # Confidence distribution
            high_conf = df[df['confidence'] >= 80].shape[0]
            med_conf = df[(df['confidence'] >= 65) & (df['confidence'] < 80)].shape[0]
            low_conf = df[df['confidence'] < 65].shape[0]
            
            print(f"\nConfidence Distribution:")
            print(f"  High (≥80%): {high_conf} ({high_conf/total_records*100:.1f}%)")
            print(f"  Medium (65-79%): {med_conf} ({med_conf/total_records*100:.1f}%)")
            print(f"  Low (<65%): {low_conf} ({low_conf/total_records*100:.1f}%)")
        
        # Text quality indicators
        if 'raw_text' in df.columns:
            text_col = 'raw_text'
        elif 'formatted_text' in df.columns:
            text_col = 'formatted_text'
        else:
            print("❌ No text column found for quality analysis")
            return
        
        # Identify quality issues
        issues = {
            'very_short': 0,
            'garbled': 0,
            'repeated_chars': 0,
            'special_chars': 0,
            'empty_text': 0
        }
        
        problematic_files = []
        
        for idx, row in df.iterrows():
            text = str(row[text_col])
            filename = row.get('filename', f'Row_{idx}')
            
            # Check for issues
            if len(text.strip()) == 0:
                issues['empty_text'] += 1
                problematic_files.append((filename, 'Empty text'))
            elif len(text.strip()) < 10:
                issues['very_short'] += 1
                problematic_files.append((filename, 'Very short text'))
            elif re.search(r'(.)\1{4,}', text):  # 5 or more repeated characters
                issues['repeated_chars'] += 1
                problematic_files.append((filename, 'Repeated characters'))
            elif len(re.findall(r'[^\w\s.,!?;:-]', text)) > len(text) * 0.2:  # >20% special chars
                issues['special_chars'] += 1
                problematic_files.append((filename, 'Too many special characters'))
            elif re.search(r'\b[a-z]{1,2}\b.*\b[a-z]{1,2}\b.*\b[a-z]{1,2}\b', text.lower()):  # Many 1-2 char words
                issues['garbled'] += 1
                problematic_files.append((filename, 'Potentially garbled'))
        
        print(f"\n🚨 Quality Issues Found:")
        print(f"  Empty text: {issues['empty_text']}")
        print(f"  Very short text (<10 chars): {issues['very_short']}")
        print(f"  Repeated characters: {issues['repeated_chars']}")
        print(f"  Too many special chars: {issues['special_chars']}")
        print(f"  Potentially garbled: {issues['garbled']}")
        
        total_issues = sum(issues.values())
        print(f"\nTotal problematic records: {total_issues} ({total_issues/total_records*100:.1f}%)")
        
        # Show worst examples
        if problematic_files:
            print(f"\n🔍 Examples of problematic files:")
            for filename, issue in problematic_files[:10]:  # Show first 10
                print(f"  {filename}: {issue}")
            if len(problematic_files) > 10:
                print(f"  ... and {len(problematic_files) - 10} more")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if total_issues > total_records * 0.2:  # >20% issues
            print("  ⚠️  High error rate detected - consider reprocessing with enhanced settings")
        if 'confidence' in df.columns and df['confidence'].mean() < 70:
            print("  📸 Low average confidence - images may need better preprocessing")
        if issues['garbled'] > total_records * 0.1:  # >10% garbled
            print("  🔧 Many garbled results - try different OCR settings or image enhancement")
        
        return {
            'total_records': total_records,
            'confidence_stats': df['confidence'].describe().to_dict() if 'confidence' in df.columns else None,
            'quality_issues': issues,
            'issue_rate': total_issues / total_records
        }
        
    except Exception as e:
        print(f"❌ Error analyzing file: {e}")
        return None


def find_ocr_files():
    """Find OCR result CSV files"""
    output_dir = Path("output")
    if not output_dir.exists():
        print("❌ Output directory not found")
        return []
    
    csv_files = list(output_dir.glob("*ocr*.csv"))
    csv_files.extend(output_dir.glob("enhanced_*.csv"))
    csv_files.extend(output_dir.glob("harper_*.csv"))
    
    return sorted(csv_files, key=lambda x: x.stat().st_mtime, reverse=True)


def main():
    """Main function"""
    print("🔍 OCR Quality Assessment Tool")
    print("=" * 40)
    
    # Find available OCR files
    ocr_files = find_ocr_files()
    
    if not ocr_files:
        print("❌ No OCR result files found in output directory")
        return
    
    print(f"Found {len(ocr_files)} OCR result files:")
    for i, file in enumerate(ocr_files, 1):
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"  {i}. {file.name} ({size_mb:.1f} MB)")
    
    try:
        choice = input(f"\nSelect file to analyze (1-{len(ocr_files)}, or 'all'): ").lower()
        
        if choice == 'all':
            for file in ocr_files:
                analyze_ocr_quality(file)
                print("\n" + "="*60 + "\n")
        else:
            file_idx = int(choice) - 1
            if 0 <= file_idx < len(ocr_files):
                analyze_ocr_quality(ocr_files[file_idx])
            else:
                print("❌ Invalid selection")
    
    except ValueError:
        print("❌ Invalid input")
    except KeyboardInterrupt:
        print("\n👋 Analysis cancelled")


if __name__ == "__main__":
    main()