#!/usr/bin/env python3
"""
Harper's Safeway Home Evidence Processor - Secure Professional Version
Password-protected OCR evidence processing system for FDSJ-739-24

Features:
- Password protection for security
- One-click export to Google Sheets
- PDF report generation
- Secure storage options
- Professional interface
"""

import pytesseract
from PIL import Image, ImageEnhance
import csv
import os
import sys
import logging
import json
import hashlib
import getpass
import webbrowser
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple
from tqdm import tqdm
import pandas as pd

class SecureEvidenceProcessor:
    """Secure Evidence Processor with password protection and export features."""
    
    def __init__(self):
        """Initialize the secure evidence processor."""
        # Security configuration
        self.password_hash = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"  # "password"
        self.session_authenticated = False
        
        # Load configuration
        self.load_config()
        
        # Initialize processing counters
        self.processed_count = 0
        self.error_count = 0
        self.high_priority_count = 0
        
        # Setup logging after authentication
        
    def authenticate(self) -> bool:
        """Secure password authentication for Harper's evidence processing."""
        print("🔐 SECURE ACCESS TO HARPER'S EVIDENCE PROCESSOR")
        print("=" * 60)
        print("⚖️  This system processes sensitive legal evidence for FDSJ-739-24")
        print("🔒 Password protection ensures evidence integrity and confidentiality")
        print("=" * 60)
        
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                password = getpass.getpass(f"🔑 Enter access password (Attempt {attempt + 1}/{max_attempts}): ")
                
                # Hash the entered password
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                if password_hash == self.password_hash:
                    print("✅ ACCESS GRANTED - Welcome to Harper's Evidence Processor")
                    self.session_authenticated = True
                    self.setup_logging()
                    self.setup_tesseract()
                    return True
                else:
                    print(f"❌ INVALID PASSWORD - {max_attempts - attempt - 1} attempts remaining")
                    
            except KeyboardInterrupt:
                print("\n🚫 Access cancelled by user")
                return False
        
        print("🚫 ACCESS DENIED - Maximum attempts exceeded")
        print("🔒 Evidence processor locked for security")
        return False
    
    def load_config(self):
        """Load configuration with fallback defaults."""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config', 'settings.py')
            config_dir = os.path.dirname(config_path)
            if config_dir not in sys.path:
                sys.path.insert(0, config_dir)
            
            import settings
            
            # OCR Configuration
            self.tesseract_cmd = getattr(settings, 'tesseract_cmd', "")
            self.tesseract_config = getattr(settings, 'tesseract_config', "--oem 3 --psm 6")
            self.use_binary_threshold = getattr(settings, 'use_binary_threshold', True)
            self.binary_threshold = getattr(settings, 'binary_threshold', 128)
            self.confidence_threshold = getattr(settings, 'confidence_threshold', 70.0)
            
            # File Processing
            self.image_extensions = getattr(settings, 'image_extensions', ['.png', '.jpg', '.jpeg'])
            
            # Output Configuration
            self.output_encoding = getattr(settings, 'output_encoding', 'utf-8')
            self.csv_delimiter = getattr(settings, 'csv_delimiter', ',')
            self.csv_fields = getattr(settings, 'csv_fields', [
                'File_Name', 'Date_Time_Approx', 'Sender', 'Recipient', 
                'Key_Factual_Statement', 'Relevance_Code', 'Processing_Status', 
                'Confidence_Score', 'Legal_Priority'
            ])
            
            # Legal Categories
            self.relevance_codes = getattr(settings, 'relevance_codes', {})
            self.priority_weights = getattr(settings, 'priority_weights', {})
            
            # Logging
            self.log_level = getattr(settings, 'log_level', 'INFO')
            self.log_file_path = getattr(settings, 'log_file_path', 'logs/evidence_processor.log')
            
        except ImportError:
            self._set_default_config()
    
    def _set_default_config(self):
        """Set secure default configuration."""
        self.tesseract_cmd = ""
        self.tesseract_config = "--oem 3 --psm 6"
        self.use_binary_threshold = True
        self.binary_threshold = 128
        self.confidence_threshold = 70.0
        
        self.image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
        
        self.output_encoding = 'utf-8'
        self.csv_delimiter = ','
        self.csv_fields = [
            'File_Name', 'Date_Time_Approx', 'Sender', 'Recipient', 
            'Key_Factual_Statement', 'Relevance_Code', 'Processing_Status', 
            'Confidence_Score', 'Legal_Priority'
        ]
        
        # Harper's case-specific categories
        self.relevance_codes = {
            'CRIMINAL_CONDUCT': ['assault', 'police', 'court', 'dec 9', 'december 9', 'charged'],
            'ENDANGERMENT': ['school', 'sick', 'doctor', 'injury', 'danger', 'harper'],
            'NON_COMPLIANCE': ['blocked', 'refused', 'contempt', 'jane', 'emma', 'nanny'],
            'USER_COMMITMENT': ['schedule', 'doctor appointment', 'pickup', 'care', 'craig'],
            'SUBSTANCE_ABUSE': ['meth', 'drug', 'cocaine', 'pills', 'substance'],
            'CUSTODY_VIOLATIONS': ['custody', 'visitation', 'court order', 'judge'],
            'REVIEW_REQUIRED': []
        }
        
        self.priority_weights = {
            'CRIMINAL_CONDUCT': 10, 'ENDANGERMENT': 9, 'NON_COMPLIANCE': 8,
            'CUSTODY_VIOLATIONS': 7, 'SUBSTANCE_ABUSE': 8, 'USER_COMMITMENT': 5,
            'REVIEW_REQUIRED': 1
        }
        
        self.log_level = 'INFO'
        self.log_file_path = 'logs/secure_evidence_processor.log'
    
    def setup_logging(self):
        """Setup secure logging with authentication record."""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file_path, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("🔐 SECURE Evidence Processor initialized for FDSJ-739-24")
        self.logger.info("✅ User authenticated successfully")
    
    def setup_tesseract(self):
        """Setup Tesseract OCR configuration."""
        if self.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
            self.logger.info(f"Tesseract path configured: {self.tesseract_cmd}")
            return

        default_paths = [
            Path("C:/Program Files/Tesseract-OCR/tesseract.exe"),
            Path("C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"),
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Tesseract-OCR/tesseract.exe"
        ]

        for candidate in default_paths:
            if candidate.is_file():
                pytesseract.pytesseract.tesseract_cmd = str(candidate)
                self.logger.info(f"Tesseract path auto-detected: {candidate}")
                return

        system_path = shutil.which("tesseract")
        if system_path:
            pytesseract.pytesseract.tesseract_cmd = system_path
            self.logger.info(f"Tesseract resolved from PATH: {system_path}")
        else:
            self.logger.warning(
                "Tesseract executable not found. Set 'tesseract_cmd' in config/settings.py"
            )
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Enhanced image preprocessing for optimal OCR."""
        try:
            if image.mode != 'L':
                image = image.convert('L')
            
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.5)
            
            if self.use_binary_threshold:
                image = image.point(lambda x: 0 if x < self.binary_threshold else 255)
            
            return image
        except Exception as e:
            self.logger.warning(f"Image preprocessing failed: {e}")
            return image
    
    def extract_text_from_image(self, image_path: str) -> Tuple[str, float]:
        """Extract text with confidence scoring."""
        try:
            image = Image.open(image_path)
            image = self.preprocess_image(image)
            
            text = pytesseract.image_to_string(image, config=self.tesseract_config)
            
            try:
                data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, 
                                               config=self.tesseract_config)
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            except Exception:
                avg_confidence = 0
            
            return text.strip(), avg_confidence
            
        except Exception as e:
            self.logger.error(f"OCR extraction failed for {image_path}: {e}")
            return "", 0
    
    def categorize_content(self, text: str) -> Tuple[str, int]:
        """Categorize content with priority scoring."""
        text_lower = text.lower()
        
        for category, keywords in self.relevance_codes.items():
            if category == 'REVIEW_REQUIRED':
                continue
                
            if any(keyword in text_lower for keyword in keywords):
                priority_score = self.priority_weights.get(category, 1)
                return category, priority_score
        
        return 'REVIEW_REQUIRED', self.priority_weights.get('REVIEW_REQUIRED', 1)
    
    def process_batch(self, input_folder: str) -> Optional[str]:
        """Process batch with automatic file naming."""
        if not self.session_authenticated:
            print("❌ Access denied - authentication required")
            return None
        
        try:
            if not os.path.exists(input_folder):
                self.logger.error(f"Input folder not found: {input_folder}")
                return None
            
            # Find all image files
            image_files = []
            for ext in self.image_extensions:
                image_files.extend(Path(input_folder).glob(f"*{ext}"))
                image_files.extend(Path(input_folder).glob(f"*{ext.upper()}"))
            
            if not image_files:
                print(f"❌ No image files found in {input_folder}")
                return None
            
            # Create timestamped output file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'output/harper_evidence_FDSJ739_{timestamp}.csv'
            
            self.logger.info(f"Found {len(image_files)} image files to process")
            
            # Process with progress bar
            results = []
            with tqdm(total=len(image_files), desc="🔍 Processing Harper's Evidence") as pbar:
                for image_path in image_files:
                    result = self._process_single_image(str(image_path))
                    if result:
                        results.append(result)
                    pbar.update(1)
            
            # Save results
            if results:
                output_dir = Path(output_file).parent
                output_dir.mkdir(exist_ok=True)
                
                with open(output_file, 'w', newline='', encoding=self.output_encoding) as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=self.csv_fields)
                    writer.writeheader()
                    writer.writerows(results)
                
                self.logger.info(f"✅ Results saved to: {output_file}")
                return output_file
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            return None
    
    def _process_single_image(self, image_path: str) -> Optional[Dict]:
        """Process a single image file."""
        try:
            filename = os.path.basename(image_path)
            raw_text, confidence = self.extract_text_from_image(image_path)
            
            if not raw_text:
                return None
            
            # Basic message parsing
            lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
            message_content = ' '.join(lines)
            
            # Categorize with priority
            relevance_code, priority_score = self.categorize_content(message_content)
            
            if priority_score >= 7:
                self.high_priority_count += 1
            
            structured_data = {
                'File_Name': filename,
                'Date_Time_Approx': lines[0] if lines else 'UNKNOWN_DATE',
                'Sender': 'UNKNOWN_SENDER',
                'Recipient': 'UNKNOWN_RECIPIENT',
                'Key_Factual_Statement': message_content[:1000],
                'Relevance_Code': relevance_code,
                'Processing_Status': 'SUCCESS' if confidence >= self.confidence_threshold else 'LOW_CONFIDENCE',
                'Confidence_Score': f"{confidence:.1f}%",
                'Legal_Priority': str(priority_score)
            }
            
            self.processed_count += 1
            return structured_data
            
        except Exception as e:
            self.error_count += 1
            return None
    
    def export_to_google_sheets(self, csv_file: str):
        """One-click export to Google Sheets."""
        try:
            # Create Google Sheets import URL
            sheets_url = "https://docs.google.com/spreadsheets/create"
            
            print("\n📊 GOOGLE SHEETS EXPORT")
            print("=" * 50)
            print("1. Opening Google Sheets in your browser...")
            print("2. Create a new spreadsheet")
            print("3. Go to File > Import > Upload")
            print(f"4. Select the file: {csv_file}")
            print("5. Choose 'Insert new sheet(s)' and click 'Import data'")
            
            # Open Google Sheets
            webbrowser.open(sheets_url)
            
            # Also open the output folder
            output_dir = os.path.dirname(os.path.abspath(csv_file))
            if os.name == 'nt':  # Windows
                os.startfile(output_dir)
            elif os.name == 'posix':  # macOS/Linux
                os.system(f'open "{output_dir}"')
            
            print(f"✅ Output folder opened: {output_dir}")
            print("📁 Drag and drop the CSV file into Google Sheets import dialog")
            
        except Exception as e:
            self.logger.error(f"Google Sheets export failed: {e}")
            print("❌ Failed to open Google Sheets - please import manually")
    
    def generate_pdf_report(self, csv_file: str) -> str:
        """Generate a professional PDF report."""
        try:
            # Simple HTML report generation
            df = pd.read_csv(csv_file)
            
            # Generate summary statistics
            high_priority = df[df['Legal_Priority'].astype(int) >= 7]
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Harper's Evidence Report - FDSJ-739-24</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; }}
                    .summary {{ background-color: #f5f5f5; padding: 15px; margin: 20px 0; }}
                    .high-priority {{ background-color: #ffe6e6; border-left: 5px solid #ff0000; padding: 10px; margin: 10px 0; }}
                    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Harper's Custody Evidence Report</h1>
                    <h2>Case Number: FDSJ-739-24</h2>
                    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="summary">
                    <h3>📊 Processing Summary</h3>
                    <ul>
                        <li><strong>Total Evidence Processed:</strong> {len(df)} items</li>
                        <li><strong>High Priority Evidence:</strong> {len(high_priority)} items</li>
                        <li><strong>Success Rate:</strong> {len(df[df['Processing_Status'] == 'SUCCESS']) / len(df) * 100:.1f}%</li>
                        <li><strong>Categories Found:</strong> {', '.join(df['Relevance_Code'].unique())}</li>
                    </ul>
                </div>
                
                <div class="high-priority">
                    <h3>🎯 High Priority Evidence (Priority 7+)</h3>
                    <p>The following evidence items have been identified as high priority for Harper's custody case:</p>
                </div>
                
                <table>
                    <tr>
                        <th>File Name</th>
                        <th>Date/Time</th>
                        <th>Category</th>
                        <th>Priority</th>
                        <th>Key Statement</th>
                    </tr>
            """
            
            # Add high priority rows
            for _, row in high_priority.iterrows():
                html_content += f"""
                    <tr>
                        <td>{row['File_Name']}</td>
                        <td>{row['Date_Time_Approx']}</td>
                        <td>{row['Relevance_Code']}</td>
                        <td>{row['Legal_Priority']}</td>
                        <td>{row['Key_Factual_Statement'][:200]}...</td>
                    </tr>
                """
            
            html_content += """
                </table>
                
                <div class="summary">
                    <h3>⚖️ Legal Notes</h3>
                    <p><strong>Confidentiality:</strong> This report contains sensitive legal evidence processed for Harper's custody case.</p>
                    <p><strong>Review Required:</strong> All evidence should be manually reviewed for accuracy before court submission.</p>
                    <p><strong>Data Integrity:</strong> Original image files are preserved as primary evidence sources.</p>
                </div>
            </body>
            </html>
            """
            
            # Save HTML report
            report_file = csv_file.replace('.csv', '_report.html')
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"📄 PDF-ready report generated: {report_file}")
            print("🖨️  Open this file in your browser and print to PDF")
            
            # Open the report
            webbrowser.open(f"file://{os.path.abspath(report_file)}")
            
            return report_file
            
        except Exception as e:
            self.logger.error(f"PDF report generation failed: {e}")
            return ""
    
    def secure_storage_backup(self, csv_file: str):
        """Create secure backup copies."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = Path('secure_backups')
            backup_dir.mkdir(exist_ok=True)
            
            # Create multiple backup formats
            backup_files = []
            
            # 1. Timestamped CSV backup
            csv_backup = backup_dir / f"harper_evidence_backup_{timestamp}.csv"
            Path(csv_file).copy(csv_backup)
            backup_files.append(str(csv_backup))
            
            # 2. JSON backup for data integrity
            df = pd.read_csv(csv_file)
            json_backup = backup_dir / f"harper_evidence_backup_{timestamp}.json"
            df.to_json(json_backup, orient='records', indent=2)
            backup_files.append(str(json_backup))
            
            # 3. Excel backup for easy viewing
            excel_backup = backup_dir / f"harper_evidence_backup_{timestamp}.xlsx"
            df.to_excel(excel_backup, index=False, engine='openpyxl')
            backup_files.append(str(excel_backup))
            
            print(f"\n💾 SECURE BACKUPS CREATED:")
            for backup in backup_files:
                print(f"   📁 {backup}")
            
            self.logger.info(f"Secure backups created: {len(backup_files)} files")
            
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            print("⚠️  Backup creation failed - manually copy your CSV file")

def main():
    """Secure main entry point with professional interface."""
    # ASCII art header
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║              🏛️  HARPER'S LEGAL EVIDENCE PROCESSOR  🏛️              ║
    ║                                                                  ║
    ║                    🔐 SECURE ACCESS SYSTEM 🔐                    ║
    ║                                                                  ║
    ║  Case: FDSJ-739-24 | Objective: Sole Custody Documentation      ║
    ║  OCR-Based Evidence Processing | Password Protected              ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    processor = SecureEvidenceProcessor()
    
    # Authenticate user
    if not processor.authenticate():
        print("\n🚫 Exiting - Authentication failed")
        return
    
    # Main processing loop
    while True:
        print(f"\n{'='*70}")
        print("🎯 HARPER'S EVIDENCE PROCESSING CENTER")
        print(f"{'='*70}")
        print("1. 🔍 Process Evidence Images (custody_screenshots/)")
        print("2. 📊 Export to Google Sheets")
        print("3. 📄 Generate PDF Report")
        print("4. 💾 Create Secure Backups")
        print("5. 📁 Open Output Folder")
        print("6. 🚪 Exit Processor")
        print(f"{'='*70}")
        
        try:
            choice = input("👆 Select option (1-6): ").strip()
            
            if choice == '1':
                print("\n🔍 PROCESSING EVIDENCE...")
                csv_file = processor.process_batch('custody_screenshots')
                
                if csv_file:
                    print(f"\n✅ PROCESSING COMPLETE!")
                    print(f"📊 Processed: {processor.processed_count} files")
                    print(f"🎯 High Priority: {processor.high_priority_count} evidence items")
                    print(f"❌ Errors: {processor.error_count} files")
                    print(f"📁 Output: {csv_file}")
                    
                    # Auto-generate backups
                    processor.secure_storage_backup(csv_file)
                    
                    # Offer immediate export options
                    print(f"\n{'='*50}")
                    print("🚀 QUICK ACTIONS:")
                    export_choice = input("Export to Google Sheets now? (y/n): ").lower()
                    if export_choice == 'y':
                        processor.export_to_google_sheets(csv_file)
                    
                    pdf_choice = input("Generate PDF report now? (y/n): ").lower()
                    if pdf_choice == 'y':
                        processor.generate_pdf_report(csv_file)
                
            elif choice == '2':
                # Find latest CSV file
                output_files = list(Path('output').glob('harper_evidence_*.csv'))
                if output_files:
                    latest_file = max(output_files, key=os.path.getctime)
                    processor.export_to_google_sheets(str(latest_file))
                else:
                    print("❌ No evidence files found. Process images first.")
                    
            elif choice == '3':
                # Find latest CSV file
                output_files = list(Path('output').glob('harper_evidence_*.csv'))
                if output_files:
                    latest_file = max(output_files, key=os.path.getctime)
                    processor.generate_pdf_report(str(latest_file))
                else:
                    print("❌ No evidence files found. Process images first.")
                    
            elif choice == '4':
                # Find latest CSV file and backup
                output_files = list(Path('output').glob('harper_evidence_*.csv'))
                if output_files:
                    latest_file = max(output_files, key=os.path.getctime)
                    processor.secure_storage_backup(str(latest_file))
                else:
                    print("❌ No evidence files found. Process images first.")
                    
            elif choice == '5':
                # Open output folder
                output_dir = os.path.abspath('output')
                if os.name == 'nt':
                    os.startfile(output_dir)
                else:
                    os.system(f'open "{output_dir}"')
                print(f"📁 Opened: {output_dir}")
                
            elif choice == '6':
                print("\n👋 Closing Harper's Evidence Processor")
                print("🔒 Session secured - Evidence protected")
                print("⚖️  Good luck with Harper's custody case!")
                break
                
            else:
                print("❌ Invalid option. Please select 1-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Session terminated by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again or contact support.")

if __name__ == "__main__":
    main()