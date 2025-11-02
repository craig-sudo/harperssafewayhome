#!/usr/bin/env python3
"""
Smart Evidence Renamer for Harper's Custody Case
Intelligently renames files based on OCR content, people involved, and context
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
import pytesseract
from PIL import Image
import pandas as pd
from utils.path_utils import safe_filename, ensure_long_path

class SmartEvidenceRenamer:
    def __init__(self):
        self.case_number = "FDSJ-739-24"
        self.processed_count = 0
        self.renamed_count = 0
        
        # Key people in Harper's case
        self.people_database = {
            'emma_ryan': {
                'names': ['emma ryan', 'emma elizabeth', 'emma', 'em'],
                'phone': '5062910202',
                'relationship': 'mom',
                'context': 'Messages between Emma (mom) and Dad'
            },
            'matt_ryan': {
                'names': ['matt ryan', 'matthew ryan', 'matt', 'matthew'],
                'phone': None,
                'relationship': 'unknown_male',
                'context': 'Messages between Matt and Dad'
            },
            'cole_brook': {
                'names': ['cole brook', 'cole', 'brook'],
                'phone': None,
                'relationship': 'emma_contact',
                'context': 'Messages between Cole and Emma'
            },
            'tony_baker': {
                'names': ['tony baker', 'tony', 'baker'],
                'phone': None,
                'relationship': 'emma_contact', 
                'context': 'Messages between Tony and Emma'
            },
            'harper': {
                'names': ['harper'],
                'phone': None,
                'relationship': 'child',
                'context': 'References to Harper'
            }
        }
        
        # Content categories for smart naming
        self.content_categories = {
            'custody_violation': [
                'custody violation', 'not returning', 'supposed to be back', 
                'pickup time', 'drop off', 'visitation', 'custody schedule'
            ],
            'health_medical': [
                'doctor', 'medical', 'hospital', 'sick', 'injury', 'medicine',
                'prescription', 'therapy', 'counseling', 'health'
            ],
            'threatening': [
                'threat', 'kill', 'hurt', 'revenge', 'get back', 'sorry will',
                'regret', 'intimidate', 'scare', 'afraid', 'fear'
            ],
            'december_9_incident': [
                'december 9', 'dec 9', '12/9', '12-9', 'incident', 'police'
            ],
            'school_issues': [
                'school', 'teacher', 'principal', 'homework', 'attendance',
                'absent', 'tardy', 'pickup from school'
            ],
            'financial': [
                'money', 'child support', 'expenses', 'cost', 'pay for',
                'financial', 'bank', 'payment'
            ],
            'legal_court': [
                'court', 'lawyer', 'attorney', 'judge', 'legal', 'custody agreement',
                'parenting plan', 'court order'
            ]
        }

    def extract_text_from_image(self, image_path):
        """Extract text from image using OCR"""
        try:
            # Configure tesseract if needed
            if os.path.exists("C:/Program Files/Tesseract-OCR/tesseract.exe"):
                pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
            
            # Open and process image
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text
            text = pytesseract.image_to_string(image, config='--psm 6')
            return text.strip()
        
        except Exception as e:
            print(f"  ⚠️ OCR failed for {image_path.name}: {e}")
            return ""

    def identify_people_in_text(self, text):
        """Identify people mentioned in the text"""
        text_lower = text.lower()
        identified_people = []
        
        for person_id, person_info in self.people_database.items():
            # Check names
            for name in person_info['names']:
                if name.lower() in text_lower:
                    identified_people.append(person_id)
                    break
            
            # Check phone number
            if person_info['phone'] and person_info['phone'] in text:
                if person_id not in identified_people:
                    identified_people.append(person_id)
        
        return identified_people

    def categorize_content(self, text):
        """Categorize content based on keywords"""
        text_lower = text.lower()
        
        for category, keywords in self.content_categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return 'general'

    def extract_date_from_text(self, text):
        """Extract date from text content"""
        # Look for various date formats
        date_patterns = [
            r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b',  # MM/DD/YYYY or MM-DD-YYYY
            r'\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b',  # YYYY/MM/DD or YYYY-MM-DD
            r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2})\b',  # MM/DD/YY or MM-DD-YY
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    # Try to parse and format the date
                    if len(match.groups()) == 3:
                        if match.group(1).isdigit() and len(match.group(1)) == 4:  # YYYY format
                            year, month, day = match.groups()
                        elif match.group(1).isalpha():  # Month name format
                            month_name = match.group(1)
                            day = match.group(2)
                            year = match.group(3)
                            # Convert month name to number
                            month_map = {
                                'january': '01', 'jan': '01', 'february': '02', 'feb': '02',
                                'march': '03', 'mar': '03', 'april': '04', 'apr': '04',
                                'may': '05', 'june': '06', 'jun': '06', 'july': '07', 'jul': '07',
                                'august': '08', 'aug': '08', 'september': '09', 'sep': '09',
                                'october': '10', 'oct': '10', 'november': '11', 'nov': '11',
                                'december': '12', 'dec': '12'
                            }
                            month = month_map.get(month_name.lower(), '00')
                        else:  # MM/DD/YYYY format
                            month, day, year = match.groups()
                        
                        # Ensure 4-digit year
                        if len(year) == 2:
                            year = '20' + year
                        
                        return f"{year}{month.zfill(2)}{day.zfill(2)}"
                except:
                    continue
        
        return None

    def extract_date_from_filename(self, filename):
        """Extract date from filename"""
        # Look for date patterns in filename
        date_patterns = [
            r'(\d{4})[-_]?(\d{2})[-_]?(\d{2})',  # YYYY-MM-DD or YYYYMMDD
            r'(\d{2})[-_]?(\d{2})[-_]?(\d{4})',  # MM-DD-YYYY or MMDDYYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                if len(match.group(1)) == 4:  # First group is year
                    year, month, day = match.groups()
                else:  # First group is month
                    month, day, year = match.groups()
                
                return f"{year}{month.zfill(2)}{day.zfill(2)}"
        
        return None

    def generate_smart_filename(self, original_path, text_content, identified_people, category, date_str):
        """Generate intelligent filename based on analysis"""
        
        # Start building filename components
        components = []
        
        # Add people involved
        if identified_people:
            # Sort people for consistent naming
            people_names = []
            for person in identified_people:
                if person == 'emma_ryan':
                    people_names.append('emma')
                elif person == 'matt_ryan':
                    people_names.append('matt')
                elif person == 'cole_brook':
                    people_names.append('cole')
                elif person == 'tony_baker':
                    people_names.append('tony')
                elif person == 'harper':
                    people_names.append('harper')
            
            if people_names:
                components.append('-'.join(sorted(people_names)))
        
        # Add category
        if category != 'general':
            components.append(category.replace('_', '-'))
        
        # Add date
        if date_str:
            components.append(date_str)
        else:
            components.append('unknown-date')
        
        # If no meaningful components found, use generic naming
        if not components or (len(components) == 1 and components[0] == 'unknown-date'):
            components = ['evidence', 'unknown-date']
        
        # Get file extension
        original_ext = original_path.suffix.lower()
        
        # Generate base filename and enforce safety/length
        base_name = '-'.join(components)
        candidate = f"{base_name}{original_ext}"
        return safe_filename(candidate, max_len=140)

    def process_evidence_folder(self, source_folder, output_folder):
        """Process all files in evidence folder with smart renaming"""
        
        source_path = Path(source_folder)
        output_path = Path(output_folder)
        
        if not source_path.exists():
            print(f"❌ Source folder not found: {source_folder}")
            return
        
        # Create output folder
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create category subfolders
        categories = list(self.content_categories.keys()) + ['general', 'conversations']
        for category in categories:
            (output_path / category).mkdir(exist_ok=True)
        
        # Process all image files
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.heic'}
        files_to_process = []
        
        for ext in image_extensions:
            files_to_process.extend(source_path.rglob(f'*{ext}'))
            files_to_process.extend(source_path.rglob(f'*{ext.upper()}'))
        
        print(f"\n🔍 Found {len(files_to_process)} image files to process...")
        print(f"📂 Output folder: {output_folder}")
        print("=" * 60)
        
        # Track renaming for report
        renaming_log = []
        
        for file_path in files_to_process:
            try:
                self.processed_count += 1
                print(f"\n[{self.processed_count}/{len(files_to_process)}] Processing: {file_path.name}")
                
                # Extract text from image
                text_content = self.extract_text_from_image(file_path)
                
                # Analyze content
                identified_people = self.identify_people_in_text(text_content)
                category = self.categorize_content(text_content)
                
                # Extract date
                date_str = self.extract_date_from_text(text_content)
                if not date_str:
                    date_str = self.extract_date_from_filename(file_path.name)
                
                # Generate smart filename
                new_filename = self.generate_smart_filename(
                    file_path, text_content, identified_people, category, date_str
                )
                
                # Determine output subfolder
                if identified_people:
                    if len(identified_people) > 1:
                        subfolder = 'conversations'
                    else:
                        subfolder = category
                else:
                    subfolder = category
                
                # Create destination path
                dest_folder = output_path / subfolder
                dest_path = dest_folder / new_filename
                
                # Handle duplicate filenames
                counter = 1
                original_dest = dest_path
                while dest_path.exists():
                    stem = original_dest.stem
                    suffix = original_dest.suffix
                    dest_path = original_dest.parent / f"{stem}-{counter:03d}{suffix}"
                    counter += 1
                
                # Copy file with Windows long-path support
                shutil.copy2(ensure_long_path(file_path), ensure_long_path(dest_path))
                self.renamed_count += 1
                
                # Log the renaming
                renaming_log.append({
                    'original_name': file_path.name,
                    'new_name': dest_path.name,
                    'category': category,
                    'people': ', '.join(identified_people) if identified_people else 'None',
                    'date_found': date_str or 'None',
                    'subfolder': subfolder,
                    'text_sample': text_content[:100].replace('\n', ' ') if text_content else 'No text extracted'
                })
                
                print(f"  👥 People: {', '.join(identified_people) if identified_people else 'None'}")
                print(f"  📂 Category: {category}")
                print(f"  📅 Date: {date_str or 'Not found'}")
                print(f"  ✅ Renamed: {dest_path.name}")
                
            except Exception as e:
                print(f"  ❌ Error processing {file_path.name}: {e}")
        
        # Generate report
        self.generate_renaming_report(output_path, renaming_log)
        
        print("\n" + "=" * 60)
        print(f"🎉 SMART RENAMING COMPLETE!")
        print(f"📊 Total processed: {self.processed_count}")
        print(f"✅ Successfully renamed: {self.renamed_count}")
        print(f"📁 Output location: {output_folder}")
        print("=" * 60)

    def generate_renaming_report(self, output_path, renaming_log):
        """Generate detailed renaming report"""
        
        # Create DataFrame
        df = pd.DataFrame(renaming_log)
        
        # Save CSV report
        report_path = output_path / f"SMART_RENAMING_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(report_path, index=False)
        
        # Create summary report
        summary_path = output_path / "RENAMING_SUMMARY.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"HARPER'S EVIDENCE SMART RENAMING REPORT\n")
            f.write(f"Case: {self.case_number}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"PROCESSING SUMMARY:\n")
            f.write(f"Total files processed: {self.processed_count}\n")
            f.write(f"Successfully renamed: {self.renamed_count}\n")
            f.write(f"Success rate: {(self.renamed_count/self.processed_count)*100:.1f}%\n\n")
            
            # Category breakdown
            f.write("CATEGORY BREAKDOWN:\n")
            category_counts = df['category'].value_counts()
            for category, count in category_counts.items():
                f.write(f"  {category}: {count} files\n")
            f.write("\n")
            
            # People involved breakdown
            f.write("PEOPLE IDENTIFIED:\n")
            all_people = []
            for people_list in df['people']:
                if people_list != 'None':
                    all_people.extend([p.strip() for p in people_list.split(',')])
            
            if all_people:
                people_counts = pd.Series(all_people).value_counts()
                for person, count in people_counts.items():
                    f.write(f"  {person}: {count} files\n")
            else:
                f.write("  No people identified in processed files\n")
        
        print(f"\n📋 Reports saved:")
        print(f"  Detailed: {report_path}")
        print(f"  Summary: {summary_path}")


def main():
    """Main function to run smart evidence renaming"""
    
    print("🎯 HARPER'S SMART EVIDENCE RENAMER")
    print(f"Case: FDSJ-739-24")
    print("=" * 60)
    
    # Initialize renamer
    renamer = SmartEvidenceRenamer()
    
    # Set up paths
    source_folder = "custody_screenshots_organized"
    output_folder = "custody_screenshots_smart_renamed"
    
    print(f"📂 Source: {source_folder}")
    print(f"📁 Output: {output_folder}")
    
    if not os.path.exists(source_folder):
        print(f"❌ Source folder '{source_folder}' not found!")
        print("💡 Make sure you've run the evidence organizer first")
        return
    
    # Process evidence
    renamer.process_evidence_folder(source_folder, output_folder)


if __name__ == "__main__":
    main()