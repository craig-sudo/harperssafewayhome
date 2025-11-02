#!/usr/bin/env python3
"""
Harper's Evidence Timeline Generator - Creates chronological court timeline
Processes all evidence and creates a detailed timeline for legal presentation
"""

import csv
import pandas as pd
from datetime import datetime
from pathlib import Path
import re
import json
from collections import defaultdict

class EvidenceTimelineGenerator:
    """Creates comprehensive chronological timeline of all evidence"""
    
    def __init__(self):
        self.output_folder = Path("output")
        self.timeline_data = []
        
        print("""
╔══════════════════════════════════════════════════════════════════╗
║           📅 HARPER'S EVIDENCE TIMELINE GENERATOR 📅            ║
║                                                                  ║
║  🕒 Chronological Analysis for Court Presentation               ║
║  📋 Case: FDSJ-739-24 | Timeline Evidence Builder              ║
╚══════════════════════════════════════════════════════════════════╝
        """)
    
    def parse_date_from_filename(self, filename):
        """Extract dates from various filename formats"""
        # Try different date patterns
        patterns = [
            r'(\d{4}-\d{2}-\d{2})',      # 2024-12-09
            r'(\d{8})',                   # 20241209
            r'(\d{2}/\d{2}/\d{4})',      # 12/09/2024
            r'(\d{2}-\d{2}-\d{4})',      # 12-09-2024
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                date_str = match.group(1)
                try:
                    if '-' in date_str and len(date_str) == 10:
                        return datetime.strptime(date_str, '%Y-%m-%d')
                    elif len(date_str) == 8 and date_str.isdigit():
                        return datetime.strptime(date_str, '%Y%m%d')
                    elif '/' in date_str:
                        return datetime.strptime(date_str, '%m/%d/%Y')
                    elif '-' in date_str:
                        return datetime.strptime(date_str, '%m-%d-%Y')
                except:
                    continue
        
        return None
    
    def categorize_by_severity(self, categories, key_phrases, priority):
        """Categorize evidence by legal severity"""
        if priority == "CRITICAL" or "december-9" in categories.lower():
            return "🚨 CRITICAL INCIDENT"
        elif "threatening" in categories.lower() or any(word in key_phrases.lower() for word in ["threat", "kill", "hurt"]):
            return "⚠️ THREATENING BEHAVIOR"
        elif "custody-violation" in categories.lower():
            return "🔒 CUSTODY VIOLATION"
        elif "health-medical" in categories.lower():
            return "🏥 MEDICAL/HEALTH"
        elif "legal-court" in categories.lower():
            return "⚖️ LEGAL PROCEEDINGS"
        elif "financial" in categories.lower():
            return "💰 FINANCIAL"
        else:
            return "📋 GENERAL EVIDENCE"
    
    def process_csv_files(self):
        """Process all CSV evidence files and extract timeline data"""
        csv_files = list(self.output_folder.glob("harper_*.csv"))
        
        for csv_file in csv_files:
            print(f"📊 Processing: {csv_file.name}")
            
            try:
                df = pd.read_csv(csv_file)
                
                for _, row in df.iterrows():
                    # Extract date from filename or date fields
                    date_obj = None
                    
                    if 'date_extracted' in row and pd.notna(row['date_extracted']):
                        date_str = str(row['date_extracted'])
                        if date_str != "unknown" and len(date_str) == 8:
                            try:
                                date_obj = datetime.strptime(date_str, '%Y%m%d')
                            except:
                                pass
                    
                    if not date_obj:
                        date_obj = self.parse_date_from_filename(row['filename'])
                    
                    # If still no date, try created/modified dates
                    if not date_obj and 'date_created' in row and pd.notna(row['date_created']):
                        try:
                            date_obj = pd.to_datetime(row['date_created'])
                        except:
                            pass
                    
                    # Create timeline entry
                    severity = self.categorize_by_severity(
                        row.get('categories', ''),
                        row.get('key_phrases', ''),
                        row.get('priority', '')
                    )
                    
                    timeline_entry = {
                        'date': date_obj if date_obj else datetime(2024, 1, 1),  # Default date if none found
                        'date_str': date_obj.strftime('%Y-%m-%d') if date_obj else "Unknown Date",
                        'filename': row['filename'],
                        'severity': severity,
                        'priority': row.get('priority', 'MEDIUM'),
                        'categories': row.get('categories', ''),
                        'key_phrases': row.get('key_phrases', ''),
                        'people': row.get('people_mentioned', ''),
                        'text_preview': str(row.get('text_content', ''))[:200] + "..." if pd.notna(row.get('text_content')) else "",
                        'file_type': row.get('file_type', 'image'),
                        'source_csv': csv_file.name
                    }
                    
                    self.timeline_data.append(timeline_entry)
                    
            except Exception as e:
                print(f"❌ Error processing {csv_file}: {e}")
    
    def generate_timeline_report(self):
        """Generate comprehensive timeline report"""
        if not self.timeline_data:
            print("❌ No timeline data found")
            return
        
        # Sort by date
        self.timeline_data.sort(key=lambda x: x['date'])
        
        # Generate timeline CSV
        timeline_csv = self.output_folder / f"harper_evidence_timeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(timeline_csv, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['date', 'severity', 'filename', 'priority', 'people', 'key_phrases', 'text_preview', 'categories']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for entry in self.timeline_data:
                writer.writerow({
                    'date': entry['date_str'],
                    'severity': entry['severity'], 
                    'filename': entry['filename'],
                    'priority': entry['priority'],
                    'people': entry['people'],
                    'key_phrases': entry['key_phrases'],
                    'text_preview': entry['text_preview'],
                    'categories': entry['categories']
                })
        
        # Generate summary statistics
        severity_counts = defaultdict(int)
        monthly_counts = defaultdict(int)
        people_counts = defaultdict(int)
        
        for entry in self.timeline_data:
            severity_counts[entry['severity']] += 1
            month_key = entry['date'].strftime('%Y-%m') if entry['date'].year > 2020 else "Unknown"
            monthly_counts[month_key] += 1
            
            if entry['people']:
                for person in entry['people'].split(';'):
                    person = person.strip()
                    if person:
                        people_counts[person] += 1
        
        # Generate beautiful report
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║              📅 HARPER'S EVIDENCE TIMELINE REPORT 📅            ║
╚══════════════════════════════════════════════════════════════════╝

📊 TIMELINE ANALYSIS:
   📋 Total Evidence Items: {len(self.timeline_data):,}
   📅 Date Range: {min(self.timeline_data, key=lambda x: x['date'])['date_str']} to {max(self.timeline_data, key=lambda x: x['date'])['date_str']}

🚨 EVIDENCE BY SEVERITY:""")
        
        for severity, count in sorted(severity_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {severity}: {count:,} items")
        
        print(f"""
👥 EVIDENCE BY PERSON:""")
        for person, count in sorted(people_counts.items(), key=lambda x: x[1], reverse=True):
            if count > 5:  # Only show significant mentions
                print(f"   {person}: {count:,} mentions")
        
        print(f"""
📈 MONTHLY EVIDENCE DISTRIBUTION:""")
        for month, count in sorted(monthly_counts.items(), reverse=True)[:12]:  # Last 12 months
            if month != "Unknown":
                print(f"   {month}: {count:,} items")
        
        print(f"""
💾 TIMELINE SAVED TO: {timeline_csv.name}

🎯 This timeline provides:
   • Chronological evidence sequence
   • Severity-based organization  
   • Person-specific evidence tracking
   • Monthly incident patterns
   • Court-ready presentation format

📋 Use this timeline to show the court:
   • Pattern of escalating behavior
   • Frequency of incidents
   • Timeline of custody violations
   • Evidence of threatening behavior
        """)
        
        return timeline_csv

def main():
    """Main function"""
    try:
        generator = EvidenceTimelineGenerator()
        generator.process_csv_files()
        generator.generate_timeline_report()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()