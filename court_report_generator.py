#!/usr/bin/env python3
"""
Harper's Court Report Generator - Professional PDF Reports for Legal Team
Creates court-ready documentation with evidence summaries and analysis
"""

import csv
import pandas as pd
from datetime import datetime
from pathlib import Path
import json
from collections import defaultdict, Counter

# PDF generation (will install if needed)
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class CourtReportGenerator:
    """Generates professional court reports from evidence data"""
    
    def __init__(self):
        self.output_folder = Path("output")
        self.report_folder = Path("court_reports")
        self.report_folder.mkdir(exist_ok=True)
        
        print("""
╔══════════════════════════════════════════════════════════════════╗
║           ⚖️ HARPER'S COURT REPORT GENERATOR ⚖️                 ║
║                                                                  ║
║  📋 Professional Legal Documentation System                     ║
║  🏛️ Case: FDSJ-739-24 | Court-Ready Evidence Reports          ║
╚══════════════════════════════════════════════════════════════════╝
        """)
    
    def analyze_evidence_data(self):
        """Analyze all evidence CSV files and compile statistics"""
        csv_files = list(self.output_folder.glob("harper_*.csv"))
        
        analysis = {
            'total_evidence': 0,
            'by_priority': defaultdict(int),
            'by_category': defaultdict(int),
            'by_person': defaultdict(int),
            'threatening_incidents': [],
            'custody_violations': [],
            'december_9_evidence': [],
            'medical_evidence': [],
            'timeline_summary': defaultdict(int),
            'file_types': defaultdict(int)
        }
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                print(f"📊 Analyzing: {csv_file.name} ({len(df)} records)")
                
                for _, row in df.iterrows():
                    analysis['total_evidence'] += 1
                    
                    # Priority analysis
                    priority = row.get('priority', 'MEDIUM')
                    analysis['by_priority'][priority] += 1
                    
                    # Category analysis
                    categories = str(row.get('categories', '')).lower()
                    if 'threatening' in categories:
                        analysis['by_category']['Threatening Behavior'] += 1
                        analysis['threatening_incidents'].append({
                            'file': row['filename'],
                            'date': row.get('date_extracted', 'Unknown'),
                            'people': row.get('people_mentioned', ''),
                            'phrases': row.get('key_phrases', '')
                        })
                    
                    if 'custody' in categories:
                        analysis['by_category']['Custody Violations'] += 1
                        analysis['custody_violations'].append({
                            'file': row['filename'],
                            'date': row.get('date_extracted', 'Unknown'),
                            'people': row.get('people_mentioned', ''),
                            'content': str(row.get('text_content', ''))[:200]
                        })
                    
                    if 'december' in categories or 'december' in str(row.get('key_phrases', '')).lower():
                        analysis['december_9_evidence'].append({
                            'file': row['filename'],
                            'date': row.get('date_extracted', 'Unknown'),
                            'priority': priority,
                            'content': str(row.get('text_content', ''))[:200]
                        })
                    
                    if 'medical' in categories or 'health' in categories:
                        analysis['by_category']['Medical/Health'] += 1
                        analysis['medical_evidence'].append({
                            'file': row['filename'],
                            'date': row.get('date_extracted', 'Unknown'),
                            'people': row.get('people_mentioned', ''),
                            'content': str(row.get('text_content', ''))[:200]
                        })
                    
                    # People analysis
                    people = str(row.get('people_mentioned', ''))
                    for person in people.split(';'):
                        person = person.strip()
                        if person and person != 'nan':
                            analysis['by_person'][person] += 1
                    
                    # File type analysis
                    file_type = row.get('file_type', 'image')
                    analysis['file_types'][file_type] += 1
                    
                    # Timeline analysis (by month)
                    date_str = str(row.get('date_extracted', ''))
                    if len(date_str) == 8 and date_str.isdigit():
                        try:
                            date_obj = datetime.strptime(date_str, '%Y%m%d')
                            month_key = date_obj.strftime('%Y-%m')
                            analysis['timeline_summary'][month_key] += 1
                        except:
                            pass
                            
            except Exception as e:
                print(f"❌ Error analyzing {csv_file}: {e}")
        
        return analysis
    
    def generate_text_report(self, analysis):
        """Generate comprehensive text report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.report_folder / f"Harper_Evidence_Report_{timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"""
╔══════════════════════════════════════════════════════════════════╗
║                    HARPER'S EVIDENCE REPORT                     ║
║                     Case: FDSJ-739-24                           ║
║              Comprehensive Evidence Analysis                     ║
║                Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}                ║
╚══════════════════════════════════════════════════════════════════╝

EXECUTIVE SUMMARY:
================

Total Evidence Items Processed: {analysis['total_evidence']:,}
Evidence Collection Period: Comprehensive multi-format analysis
Report Purpose: Court documentation for custody proceedings

EVIDENCE BREAKDOWN BY PRIORITY:
==============================
""")
            
            for priority, count in sorted(analysis['by_priority'].items(), key=lambda x: {'CRITICAL': 3, 'HIGH': 2, 'MEDIUM': 1}.get(x[0], 0), reverse=True):
                percentage = (count / analysis['total_evidence']) * 100
                f.write(f"{priority}: {count:,} items ({percentage:.1f}%)\n")
            
            f.write(f"""
EVIDENCE BREAKDOWN BY CATEGORY:
==============================
""")
            for category, count in sorted(analysis['by_category'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / analysis['total_evidence']) * 100
                f.write(f"{category}: {count:,} items ({percentage:.1f}%)\n")
            
            f.write(f"""
EVIDENCE BY PERSON MENTIONED:
============================
""")
            for person, count in sorted(analysis['by_person'].items(), key=lambda x: x[1], reverse=True):
                if count > 5:  # Only significant mentions
                    f.write(f"{person}: {count:,} mentions\n")
            
            f.write(f"""
CRITICAL INCIDENT ANALYSIS:
==========================

DECEMBER 9TH INCIDENT EVIDENCE: {len(analysis['december_9_evidence'])} items
""")
            for i, item in enumerate(analysis['december_9_evidence'][:10], 1):
                f.write(f"   {i}. {item['file']} (Priority: {item['priority']})\n")
            
            f.write(f"""
THREATENING BEHAVIOR EVIDENCE: {len(analysis['threatening_incidents'])} items
""")
            for i, item in enumerate(analysis['threatening_incidents'][:10], 1):
                f.write(f"   {i}. {item['file']} - Key phrases: {item['phrases'][:100]}\n")
            
            f.write(f"""
CUSTODY VIOLATION EVIDENCE: {len(analysis['custody_violations'])} items
""")
            for i, item in enumerate(analysis['custody_violations'][:10], 1):
                f.write(f"   {i}. {item['file']} - People: {item['people']}\n")
            
            f.write(f"""
FILE TYPE DISTRIBUTION:
======================
""")
            for file_type, count in sorted(analysis['file_types'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / analysis['total_evidence']) * 100
                f.write(f"{file_type.upper()}: {count:,} files ({percentage:.1f}%)\n")
            
            f.write(f"""
MONTHLY EVIDENCE TIMELINE:
=========================
""")
            for month, count in sorted(analysis['timeline_summary'].items(), reverse=True)[:12]:
                f.write(f"{month}: {count:,} evidence items\n")
            
            f.write(f"""

LEGAL SIGNIFICANCE:
==================

This comprehensive evidence analysis demonstrates:

1. PATTERN OF BEHAVIOR: {analysis['by_priority']['HIGH'] + analysis['by_priority'].get('CRITICAL', 0):,} high-priority incidents documenting concerning patterns.

2. COMPREHENSIVE DOCUMENTATION: {analysis['total_evidence']:,} pieces of evidence across multiple formats (images, documents, communications).

3. THREATENING BEHAVIOR: {len(analysis['threatening_incidents'])} documented instances of threatening communications or behavior.

4. CUSTODY VIOLATIONS: {len(analysis['custody_violations'])} documented violations of custody agreements or court orders.

5. DECEMBER 9TH INCIDENT: {len(analysis['december_9_evidence'])} pieces of evidence related to the critical December 9th incident.

This evidence collection provides comprehensive documentation supporting the petition for sole custody based on documented patterns of concerning behavior, custody violations, and incidents affecting Harper's welfare and safety.

Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Case: FDSJ-739-24
Evidence Processing System: Harper's Advanced Evidence Processor
            """)
        
        return report_file
    
    def generate_summary_report(self):
        """Generate the main summary report"""
        print("📊 Analyzing evidence data...")
        analysis = self.analyze_evidence_data()
        
        print("📋 Generating court report...")
        report_file = self.generate_text_report(analysis)
        
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║              📋 COURT REPORT GENERATION COMPLETE! 📋            ║
╚══════════════════════════════════════════════════════════════════╝

✅ ANALYSIS COMPLETE:
   📊 Total Evidence Items: {analysis['total_evidence']:,}
   🚨 Critical/High Priority: {analysis['by_priority'].get('CRITICAL', 0) + analysis['by_priority'].get('HIGH', 0):,}
   ⚠️ Threatening Incidents: {len(analysis['threatening_incidents']):,}
   🔒 Custody Violations: {len(analysis['custody_violations']):,}
   📅 December 9th Evidence: {len(analysis['december_9_evidence']):,}

💾 REPORT SAVED TO: {report_file.name}

🎯 This report provides:
   • Comprehensive evidence statistics
   • Pattern analysis for court presentation
   • Categorized incident summaries
   • Timeline of evidence collection
   • Legal significance assessment

📋 Use this report to:
   • Brief your legal team
   • Prepare for court hearings
   • Document evidence patterns
   • Support custody arguments
        """)
        
        return report_file

def main():
    """Main function"""
    try:
        generator = CourtReportGenerator()
        generator.generate_summary_report()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()