#!/usr/bin/env python3
"""
Court Exhibit Finder - Helps organize evidence for custody filing
"""

import pandas as pd
import os
from datetime import datetime

class ExhibitFinder:
    def __init__(self):
        # Load latest results
        self.results_file = os.path.join('output', 'smart_ocr_results_20251025_095300.csv')
        self.df = pd.read_csv(self.results_file)
        
    def score_exhibits(self):
        """Score exhibits based on legal relevance"""
        # Base score is OCR confidence
        self.df['exhibit_score'] = self.df['confidence_score']
        
        # Analyze content for categories and scoring
        def analyze_content(text):
            score = 0
            categories = []
            
            # Handle null values
            if pd.isna(text):
                return score, ''
                
            text = str(text).lower()
            
            # Look for key phrases indicating categories
            if any(word in text for word in ['threat', 'warning', 'hurt', 'kill', 'die']):
                categories.append('Threatening')
                score += 15
                
            if any(word in text for word in ['drunk', 'alcohol', 'drugs', 'high', 'substance']):
                categories.append('Substance_Related')
                score += 15
                
            if any(word in text for word in ['custody', 'court', 'lawyer', 'attorney', 'judge']):
                categories.append('Custody_Related')
                score += 15
                
            if any(word in text for word in ['money', 'payment', 'financial', 'support']):
                categories.append('Financial')
                score += 10
                
            return score, ';'.join(categories)
        
        # Apply content analysis
        content_scores = self.df['extracted_text'].apply(analyze_content)
        self.df['content_categories'] = content_scores.apply(lambda x: x[1])
        self.df['exhibit_score'] += content_scores.apply(lambda x: x[0])
        
        # Bonus for identified parties
        def identify_sender(text):
            if pd.isna(text):
                return 'Unknown'
            text = str(text).lower()
            if any(name in text for name in ['emma', 'mother', 'mom']):
                return 'Emma (Mother)'
            elif any(name in text for name in ['craig', 'dad', 'father']):
                return 'Craig (Father)'
            return 'Unknown'
            
        # Only identify sender if not already present
        self.df.loc[self.df['sender'].isna(), 'sender'] = self.df.loc[self.df['sender'].isna(), 'extracted_text'].apply(identify_sender)
        self.df.loc[self.df['sender'] != 'Unknown', 'exhibit_score'] += 20
            
    def generate_exhibit_list(self, output_file='CUSTODY_COURT_EXHIBITS.txt'):
        """Generate organized exhibit list"""
        self.score_exhibits()
        
        # Sort by score and group by categories
        exhibits = self.df.sort_values('exhibit_score', ascending=False)
        
        # Generate report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("🏛️ CUSTODY EVIDENCE LOCATION GUIDE\n")
            f.write("Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
            
            # Organize by major categories
            major_categories = {
                'THREATENING BEHAVIOR': exhibits[exhibits['content_categories'].str.contains('Threatening', na=False)],
                'SUBSTANCE ABUSE': exhibits[exhibits['content_categories'].str.contains('Substance', na=False)],
                'CUSTODY VIOLATIONS': exhibits[exhibits['content_categories'].str.contains('Custody', na=False)],
                'FINANCIAL ISSUES': exhibits[exhibits['content_categories'].str.contains('Financial', na=False)]
            }

            # Write category-specific sections
            for category_name, category_data in major_categories.items():
                if len(category_data) > 0:
                    f.write(f"\n{category_name} EVIDENCE:\n")
                    f.write("=" * 80 + "\n")
                    
                    # Group by folder location
                    grouped = category_data.groupby(category_data['file_path'].apply(lambda x: os.path.dirname(x)))
                    
                    for folder, files in grouped:
                        f.write(f"\n📁 FOLDER: {folder}\n")
                        f.write("-" * 40 + "\n")
                        
                        for _, row in files.iterrows():
                            preview = str(row['extracted_text'])[:150].replace('\n', ' ').strip()
                            f.write(f"\n📄 {row['filename']}\n")
                            f.write(f"Context: {preview}...\n")
                            if pd.notna(row['sender']):
                                f.write(f"From: {row['sender']}\n")
                            f.write(f"Score: {row['exhibit_score']:.1f}\n")
                            f.write("\n")
            
            # Add a summary section at the end
            f.write("\n\nEVIDENCE SUMMARY:\n")
            f.write("=" * 80 + "\n")
            f.write("\nTop Evidence by Category:\n\n")
            
            for category, data in major_categories.items():
                if len(data) > 0:
                    top_items = data.nlargest(3, 'exhibit_score')
                    f.write(f"\n{category}:\n")
                    for _, row in top_items.iterrows():
                        preview = str(row['extracted_text'])[:100].replace('\n', ' ').strip()
                        f.write(f"- {row['filename']} ({row['file_path']})\n")
                        f.write(f"  Context: {preview}...\n")
                
            f.write("\nEND OF EXHIBIT LIST\n")
            
        print(f"✅ Exhibit list generated: {output_file}")
        return output_file

if __name__ == "__main__":
    finder = ExhibitFinder()
    finder.generate_exhibit_list()