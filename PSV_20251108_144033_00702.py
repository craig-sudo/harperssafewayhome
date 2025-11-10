#!/usr/bin/env python3
"""
OCR Correction Interface
Simple tool to review and correct OCR results for learning
"""

import pandas as pd
import json
import os
from pathlib import Path

class OCRCorrectionInterface:
    """Simple interface to correct OCR results"""
    
    def __init__(self):
        self.corrections_file = "output/ocr_corrections.json"
        self.corrections = self.load_corrections()
    
    def load_corrections(self):
        """Load existing corrections"""
        if os.path.exists(self.corrections_file):
            try:
                with open(self.corrections_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('corrections', {})
            except:
                pass
        return {}
    
    def save_corrections(self):
        """Save corrections to file"""
        os.makedirs("output", exist_ok=True)
        data = {
            'corrections': self.corrections,
            'patterns': {},
            'config_performance': {}
        }
        with open(self.corrections_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def review_batch(self, csv_file):
        """Review a batch CSV and collect corrections"""
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
            print(f"\n📋 Reviewing: {csv_file}")
            print(f"   {len(df)} records to review")
            
            corrections_made = 0
            
            for idx, row in df.iterrows():
                print(f"\n--- Record {idx + 1}/{len(df)} ---")
                print(f"File: {row['filename']}")
                print(f"Sender: {row['sender']} → Recipient: {row['recipient']}")
                print(f"Confidence: {row.get('confidence', 'N/A')}")
                print(f"\nExtracted Text:")
                print(f"'{row['raw_text'][:200]}{'...' if len(row['raw_text']) > 200 else ''}'")
                
                # Ask for corrections
                response = input("\nCorrect this? (y/n/skip/quit): ").lower()
                
                if response == 'quit':
                    break
                elif response == 'skip':
                    continue
                elif response == 'y':
                    print("Enter corrections (leave blank to skip field):")
                    
                    # Correct text
                    corrected_text = input(f"Corrected text: ")
                    if corrected_text.strip():
                        self.corrections[row['filename']] = {
                            'original_text': row['raw_text'],
                            'corrected_text': corrected_text,
                            'sender': row['sender'],
                            'recipient': row['recipient']
                        }
                        corrections_made += 1
                    
                    # Correct sender/recipient
                    corrected_sender = input(f"Corrected sender (current: {row['sender']}): ")
                    corrected_recipient = input(f"Corrected recipient (current: {row['recipient']}): ")
                    
                    if corrected_sender.strip() or corrected_recipient.strip():
                        if row['filename'] not in self.corrections:
                            self.corrections[row['filename']] = {
                                'original_text': row['raw_text'],
                                'corrected_text': row['raw_text'],
                                'sender': row['sender'],
                                'recipient': row['recipient']
                            }
                        
                        if corrected_sender.strip():
                            self.corrections[row['filename']]['corrected_sender'] = corrected_sender
                        if corrected_recipient.strip():
                            self.corrections[row['filename']]['corrected_recipient'] = corrected_recipient
                        
                        corrections_made += 1
            
            print(f"\n✅ Review complete! Made {corrections_made} corrections")
            self.save_corrections()
            return corrections_made
            
        except Exception as e:
            print(f"Error reviewing batch: {e}")
            return 0
    
    def apply_corrections_to_csv(self, csv_file):
        """Apply saved corrections to a CSV file"""
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
            corrections_applied = 0
            
            for idx, row in df.iterrows():
                filename = row['filename']
                if filename in self.corrections:
                    correction = self.corrections[filename]
                    
                    # Apply text correction
                    if 'corrected_text' in correction:
                        df.at[idx, 'raw_text'] = correction['corrected_text']
                        df.at[idx, 'formatted_text'] = correction['corrected_text']
                    
                    # Apply sender/recipient corrections
                    if 'corrected_sender' in correction:
                        df.at[idx, 'sender'] = correction['corrected_sender']
                    if 'corrected_recipient' in correction:
                        df.at[idx, 'recipient'] = correction['corrected_recipient']
                    
                    corrections_applied += 1
            
            # Save corrected CSV
            corrected_file = csv_file.replace('.csv', '_corrected.csv')
            df.to_csv(corrected_file, index=False, encoding='utf-8')
            print(f"✅ Applied {corrections_applied} corrections to {corrected_file}")
            return corrected_file
            
        except Exception as e:
            print(f"Error applying corrections: {e}")
            return None


def main():
    """Main interface"""
    corrector = OCRCorrectionInterface()
    
    print("🔧 OCR Correction Interface")
    print("1. Review a batch file")
    print("2. Apply corrections to CSV")
    print("3. Show correction stats")
    
    choice = input("\nChoice (1-3): ")
    
    if choice == '1':
        # List available batch files
        batch_files = list(Path("output").glob("batch_*_ocr_results_*.csv"))
        if not batch_files:
            print("No batch files found in output/")
            return
        
        print("\nAvailable batch files:")
        for i, file in enumerate(batch_files, 1):
            print(f"{i}. {file.name}")
        
        try:
            selection = int(input(f"\nSelect file (1-{len(batch_files)}): ")) - 1
            if 0 <= selection < len(batch_files):
                corrector.review_batch(batch_files[selection])
            else:
                print("Invalid selection")
        except ValueError:
            print("Invalid input")
    
    elif choice == '2':
        csv_file = input("Enter CSV file path: ")
        if os.path.exists(csv_file):
            corrector.apply_corrections_to_csv(csv_file)
        else:
            print("File not found")
    
    elif choice == '3':
        print(f"\n📊 Correction Stats:")
        print(f"   Total corrections: {len(corrector.corrections)}")
        if corrector.corrections:
            print("   Recent corrections:")
            for filename, correction in list(corrector.corrections.items())[-5:]:
                print(f"   - {filename}")


if __name__ == "__main__":
    main()