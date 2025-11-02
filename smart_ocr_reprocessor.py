#!/usr/bin/env python3
"""
Smart OCR Reprocessor
Identifies and reprocesses low-quality OCR results using enhanced preprocessing
"""

import pandas as pd
import os
from pathlib import Path
from enhanced_ocr_processor import EnhancedOCRProcessor
import json
import re
from datetime import datetime

class SmartOCRReprocessor:
    """Reprocesses problematic OCR results with enhanced settings"""
    
    def __init__(self):
        self.processor = EnhancedOCRProcessor()
        self.quality_threshold = 65  # Confidence threshold for reprocessing
        
    def identify_problem_files(self, csv_file):
        """Identify files that need reprocessing"""
        print(f"🔍 Identifying problem files in {csv_file}")
        
        df = pd.read_csv(csv_file, encoding='utf-8')
        problem_files = []
        
        for idx, row in df.iterrows():
            filename = row.get('filename', '')
            filepath = row.get('filepath', '')
            text = str(row.get('raw_text', ''))
            confidence = row.get('confidence', 100)  # Default high if no confidence
            
            # Check if file needs reprocessing
            needs_reprocess = False
            reason = []
            
            # Low confidence
            if confidence < self.quality_threshold:
                needs_reprocess = True
                reason.append(f"Low confidence ({confidence:.1f}%)")
            
            # Very short text
            if len(text.strip()) < 10:
                needs_reprocess = True
                reason.append("Very short text")
            
            # Garbled text indicators
            if re.search(r'(.)\1{4,}', text):  # Repeated characters
                needs_reprocess = True
                reason.append("Repeated characters")
            
            # Too many single/double character words (garbled)
            words = text.split()
            if len(words) > 5:
                short_words = [w for w in words if len(w) <= 2 and w.isalpha()]
                if len(short_words) > len(words) * 0.3:  # >30% very short words
                    needs_reprocess = True
                    reason.append("Many short words (garbled)")
            
            if needs_reprocess and filepath and os.path.exists(filepath):
                problem_files.append({
                    'filename': filename,
                    'filepath': filepath,
                    'original_confidence': confidence,
                    'original_text': text[:100] + "..." if len(text) > 100 else text,
                    'reasons': "; ".join(reason)
                })
        
        print(f"   Found {len(problem_files)} files needing reprocessing")
        return problem_files
    
    def reprocess_files(self, problem_files, output_file):
        """Reprocess the problematic files with enhanced settings"""
        print(f"🔄 Reprocessing {len(problem_files)} files...")
        
        results = []
        improvements = 0
        
        for i, file_info in enumerate(problem_files, 1):
            print(f"   Processing {i}/{len(problem_files)}: {file_info['filename']}")
            
            # Reprocess with enhanced settings
            new_result = self.processor.process_image(file_info['filepath'])
            
            if new_result:
                # Compare improvement
                old_confidence = file_info['original_confidence']
                new_confidence = new_result.get('confidence', 0)
                
                if new_confidence > old_confidence + 10:  # 10% improvement
                    improvements += 1
                
                # Add comparison data
                new_result['original_confidence'] = old_confidence
                new_result['confidence_improvement'] = new_confidence - old_confidence
                new_result['reprocess_reason'] = file_info['reasons']
                new_result['original_text'] = file_info['original_text']
                
                results.append(new_result)
        
        # Save results
        if results:
            df = pd.DataFrame(results)
            df['reprocessed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            
            print(f"✅ Reprocessing complete!")
            print(f"   Saved {len(results)} results to {output_file}")
            print(f"   Files with improved confidence: {improvements}")
            
            if improvements > 0:
                avg_improvement = df[df['confidence_improvement'] > 0]['confidence_improvement'].mean()
                print(f"   Average confidence improvement: +{avg_improvement:.1f}%")
        
        return results
    
    def generate_comparison_report(self, results, report_file):
        """Generate a comparison report showing improvements"""
        if not results:
            return
            
        df = pd.DataFrame(results)
        
        report = []
        report.append("# OCR Reprocessing Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append("## Summary")
        report.append(f"- Files reprocessed: {len(df)}")
        report.append(f"- Files with improved confidence: {len(df[df['confidence_improvement'] > 0])}")
        report.append(f"- Average original confidence: {df['original_confidence'].mean():.1f}%")
        report.append(f"- Average new confidence: {df['confidence'].mean():.1f}%")
        report.append("")
        
        # Top improvements
        top_improvements = df.nlargest(10, 'confidence_improvement')
        if not top_improvements.empty:
            report.append("## Top Improvements")
            for _, row in top_improvements.iterrows():
                report.append(f"- {row['filename']}: {row['original_confidence']:.1f}% → {row['confidence']:.1f}% (+{row['confidence_improvement']:.1f}%)")
            report.append("")
        
        # Files still needing review
        still_problematic = df[df['confidence'] < 65]
        if not still_problematic.empty:
            report.append("## Files Still Needing Review")
            for _, row in still_problematic.iterrows():
                report.append(f"- {row['filename']}: {row['confidence']:.1f}% confidence")
            report.append("")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print(f"📊 Comparison report saved to {report_file}")


def main():
    """Main execution"""
    reprocessor = SmartOCRReprocessor()
    
    # Find latest OCR results
    output_dir = Path("output")
    csv_files = list(output_dir.glob("enhanced_ocr_results_*.csv"))
    
    if not csv_files:
        print("❌ No enhanced OCR results found")
        return
    
    # Use most recent file
    latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
    print(f"📁 Using OCR results: {latest_file}")
    
    # Identify problem files
    problem_files = reprocessor.identify_problem_files(latest_file)
    
    if not problem_files:
        print("✅ No files need reprocessing!")
        return
    
    # Ask user if they want to proceed
    print(f"\n🤔 Found {len(problem_files)} files that could benefit from reprocessing.")
    choice = input("Proceed with reprocessing? (y/n): ").lower()
    
    if choice != 'y':
        print("👋 Reprocessing cancelled")
        return
    
    # Create output files
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_csv = output_dir / f"reprocessed_ocr_results_{timestamp}.csv"
    report_file = output_dir / f"reprocessing_report_{timestamp}.md"
    
    # Reprocess files
    results = reprocessor.reprocess_files(problem_files, output_csv)
    
    # Generate report
    if results:
        reprocessor.generate_comparison_report(results, report_file)


if __name__ == "__main__":
    main()