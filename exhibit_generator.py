#!/usr/bin/env python3
"""
Harper's Exhibit Generator
Generates court-ready PDF exhibits with SHA256 verification and chain of custody documentation.

This module creates professional PDF documents for each exhibit, including:
- Exhibit cover page with case information
- SHA256 hash verification details
- File metadata and chain of custody
- Weighted evidence score
- Content preview/summary
- Verification status and notes

Designed to be called by legal_triage_suite.py or run standalone with an exhibit index CSV.
"""

import csv
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import argparse
import logging

# Try to import reportlab; provide fallback if not installed
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.resolve()
LEGAL_OUTPUT_DIR = BASE_DIR / "legal_exhibits"
CASE_ID = "FDSJ739"


class ExhibitGenerator:
    """Generate professional PDF exhibits with SHA256 verification."""
    
    def __init__(self):
        """Initialize the exhibit generator."""
        if not REPORTLAB_AVAILABLE:
            logger.warning("ReportLab not installed. Install with: pip install reportlab")
            logger.warning("PDF generation will not be available.")
        
        LEGAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.styles = self._setup_styles() if REPORTLAB_AVAILABLE else None
    
    def _setup_styles(self):
        """Set up PDF styles."""
        styles = getSampleStyleSheet()
        
        # Custom styles
        styles.add(ParagraphStyle(
            name='ExhibitTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
            alignment=TA_CENTER
        ))
        
        styles.add(ParagraphStyle(
            name='ExhibitSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1a1a1a'),
            spaceBefore=12,
            spaceAfter=6,
            borderPadding=2
        ))
        
        styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            spaceAfter=2
        ))
        
        styles.add(ParagraphStyle(
            name='FieldValue',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=8
        ))
        
        styles.add(ParagraphStyle(
            name='HashValue',
            parent=styles['Code'],
            fontSize=8,
            textColor=colors.HexColor('#0066cc'),
            fontName='Courier',
            wordWrap='CJK'
        ))
        
        return styles
    
    def generate_exhibit_pdf(self, exhibit: Dict, output_path: Path) -> bool:
        """
        Generate a single exhibit PDF.
        
        Args:
            exhibit: Exhibit metadata dictionary
            output_path: Path for the output PDF
        
        Returns True if successful, False otherwise.
        """
        if not REPORTLAB_AVAILABLE:
            logger.error("Cannot generate PDF: ReportLab not installed")
            return False
        
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            
            story = []
            
            # --- COVER PAGE ---
            
            # Title
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph("LEGAL EXHIBIT", self.styles['ExhibitTitle']))
            story.append(Paragraph(exhibit['exhibit_name'], self.styles['ExhibitSubtitle']))
            story.append(Spacer(1, 0.3*inch))
            
            # Case information table
            # Safe numeric formatting for weighted score
            _score_raw = exhibit.get('weighted_score', 0)
            try:
                _score_val = float(_score_raw)
            except Exception:
                _score_val = 0.0

            case_data = [
                ['Case ID:', exhibit['case_id']],
                ['Exhibit Number:', str(exhibit['exhibit_number'])],
                ['Priority:', exhibit['priority']],
                ['Weighted Score:', f"{_score_val:.2f}"],
                ['Date Generated:', datetime.now().strftime('%B %d, %Y')],
            ]
            
            case_table = Table(case_data, colWidths=[2*inch, 4*inch])
            case_table.setStyle(TableStyle([
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
                ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1a1a1a')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(case_table)
            story.append(Spacer(1, 0.3*inch))
            
            # --- SHA256 VERIFICATION SECTION ---
            
            story.append(Paragraph("SHA256 CRYPTOGRAPHIC VERIFICATION", self.styles['SectionHeader']))
            story.append(Spacer(1, 0.1*inch))
            
            # Verification status box (robust defaults)
            _status = exhibit.get('verification_status', 'UNKNOWN')
            _vdate = exhibit.get('verification_date') or exhibit.get('generation_date') or ''
            if isinstance(_vdate, str):
                _vdate_disp = _vdate[:10]
            else:
                _vdate_disp = ''
            status_color = colors.green if _status == 'VERIFIED' else colors.orange
            status_data = [
                [Paragraph(f"<b>Status: {_status}</b>", self.styles['Normal'])],
                [Paragraph(f"Verified: {_vdate_disp}", self.styles['FieldLabel'])],
            ]
            status_table = Table(status_data, colWidths=[6*inch])
            status_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), status_color.clone(alpha=0.1)),
                ('BOX', (0, 0), (-1, -1), 1, status_color),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(status_table)
            story.append(Spacer(1, 0.2*inch))
            
            # Hash values
            story.append(Paragraph("Original File SHA256:", self.styles['FieldLabel']))
            if exhibit['original_hash']:
                story.append(Paragraph(f"<font name='Courier'>{exhibit['original_hash']}</font>", 
                                     self.styles['HashValue']))
            else:
                story.append(Paragraph("<i>No hash available</i>", self.styles['FieldValue']))
            
            story.append(Spacer(1, 0.1*inch))
            
            _o_hash = exhibit.get('original_hash')
            _p_hash = exhibit.get('processed_hash')
            if _p_hash and _p_hash != _o_hash:
                story.append(Paragraph("Processed File SHA256:", self.styles['FieldLabel']))
                story.append(Paragraph(f"<font name='Courier'>{_p_hash}</font>", 
                                     self.styles['HashValue']))
                story.append(Spacer(1, 0.1*inch))
            
            # Verification notes
            if exhibit.get('verification_notes'):
                story.append(Paragraph("Verification Notes:", self.styles['FieldLabel']))
                story.append(Paragraph(exhibit['verification_notes'], self.styles['FieldValue']))
            
            story.append(Spacer(1, 0.3*inch))
            
            # --- FILE METADATA SECTION ---
            
            story.append(Paragraph("FILE METADATA & CHAIN OF CUSTODY", self.styles['SectionHeader']))
            story.append(Spacer(1, 0.1*inch))
            
            metadata = [
                ['Filename:', exhibit.get('filename', 'N/A')],
                ['File Path:', exhibit.get('file_path', 'N/A')],
                ['Date Extracted:', exhibit.get('date_extracted', 'N/A')],
                ['Folder Category:', exhibit.get('folder_category', 'N/A')],
                ['Source CSV:', exhibit.get('source_csv', 'N/A')],
            ]
            
            # Add external data fields if present
            if exhibit.get('date_range'):
                metadata.append(['Date Range:', exhibit['date_range']])
            if exhibit.get('feature_count'):
                metadata.append(['Feature Count:', str(exhibit['feature_count'])])
            if exhibit.get('email_count'):
                metadata.append(['Email Count:', str(exhibit['email_count'])])
            
            metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
            metadata_table.setStyle(TableStyle([
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
                ('FONT', (1, 0), (1, -1), 'Helvetica', 9),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1a1a1a')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(metadata_table)
            story.append(Spacer(1, 0.3*inch))
            
            # --- EVIDENCE CATEGORIZATION ---
            
            story.append(Paragraph("EVIDENCE CATEGORIZATION", self.styles['SectionHeader']))
            story.append(Spacer(1, 0.1*inch))
            
            categories = exhibit.get('categories', [])
            category_text = ', '.join([c.upper() for c in categories]) if categories else 'GENERAL'
            
            cat_data = [
                ['Legal Categories:', category_text],
                ['People Mentioned:', exhibit.get('people_mentioned', 'None') or 'None'],
                ['Weighted Score:', f"{_score_val:.2f} (Priority: {exhibit['priority']})"],
            ]
            
            cat_table = Table(cat_data, colWidths=[2*inch, 4*inch])
            cat_table.setStyle(TableStyle([
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
                ('FONT', (1, 0), (1, -1), 'Helvetica', 9),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1a1a1a')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(cat_table)
            story.append(Spacer(1, 0.3*inch))
            
            # --- CONTENT PREVIEW ---
            
            if exhibit.get('text_content'):
                story.append(Paragraph("CONTENT PREVIEW", self.styles['SectionHeader']))
                story.append(Spacer(1, 0.1*inch))
                
                # Escape special characters for PDF
                content = exhibit['text_content'][:500]
                content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                
                story.append(Paragraph(content, self.styles['FieldValue']))
                
                if len(exhibit.get('text_content', '')) > 500:
                    story.append(Paragraph("<i>[Content truncated for exhibit preview]</i>", 
                                         self.styles['FieldLabel']))
            
            # --- FOOTER ---
            
            story.append(Spacer(1, 0.5*inch))
            footer_text = f"""
            <para align=center>
            <font size=8 color='#666666'>
            This exhibit was generated by Harper's Safeway Home Evidence Processing System.<br/>
            SHA256 verification ensures file integrity and authenticity.<br/>
            Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            </font>
            </para>
            """
            story.append(Paragraph(footer_text, self.styles['Normal']))
            
            # Build PDF
            doc.build(story)
            logger.info(f"Generated exhibit PDF: {output_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate PDF for {exhibit['exhibit_name']}: {e}")
            return False
    
    def generate_exhibits_from_index(self, index_path: Path, limit: Optional[int] = None) -> Dict:
        """
        Generate PDF exhibits from a master exhibit index CSV.
        
        Args:
            index_path: Path to the exhibit index CSV
            limit: Optional limit on number of PDFs to generate (for testing)
        
        Returns summary statistics dictionary.
        """
        if not REPORTLAB_AVAILABLE:
            print("\nERROR: ReportLab is not installed.")
            print("Install with: pip install reportlab")
            return {'error': 'ReportLab not available'}
        
        print("\n" + "="*70)
        print("  EXHIBIT PDF GENERATOR")
        print("="*70 + "\n")
        
        if not index_path.exists():
            print(f"ERROR: Index file not found: {index_path}")
            return {'error': 'Index file not found'}
        
        # Load exhibit index
        print(f"Loading exhibit index: {index_path.name}")
        exhibits = []
        
        try:
            with open(index_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Parse categories from string
                    if 'categories' in row:
                        row['categories'] = [c.strip() for c in row['categories'].split(';')]
                    exhibits.append(row)
        except Exception as e:
            print(f"ERROR: Failed to load index: {e}")
            return {'error': str(e)}
        
        print(f"Loaded {len(exhibits)} exhibits from index")
        
        if limit:
            exhibits = exhibits[:limit]
            print(f"Limiting to first {limit} exhibits for testing")
        
        # Generate PDFs
        print(f"\nGenerating PDF exhibits...")
        success_count = 0
        failed = []
        
        for i, exhibit in enumerate(exhibits, 1):
            exhibit_name = exhibit.get('exhibit_name', f'EXHIBIT-{i:03d}.pdf')
            output_path = LEGAL_OUTPUT_DIR / exhibit_name
            
            print(f"  [{i}/{len(exhibits)}] {exhibit_name}...", end=' ')
            
            if self.generate_exhibit_pdf(exhibit, output_path):
                print("✓")
                success_count += 1
            else:
                print("✗")
                failed.append(exhibit_name)
        
        # Summary
        print("\n" + "="*70)
        print("  GENERATION COMPLETE")
        print("="*70)
        print(f"  Total Exhibits:    {len(exhibits)}")
        print(f"  Successfully Generated: {success_count}")
        print(f"  Failed:            {len(failed)}")
        if failed:
            print(f"\n  Failed exhibits:")
            for name in failed[:10]:
                print(f"    - {name}")
            if len(failed) > 10:
                print(f"    ... and {len(failed)-10} more")
        print(f"\n  Output Directory:  {LEGAL_OUTPUT_DIR}")
        print("="*70 + "\n")
        
        return {
            'total': len(exhibits),
            'success': success_count,
            'failed': len(failed),
            'output_dir': str(LEGAL_OUTPUT_DIR)
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Harper's Exhibit Generator - Create court-ready PDF exhibits",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--index', type=str, required=True,
                       help='Path to exhibit index CSV file')
    parser.add_argument('--limit', type=int,
                       help='Limit number of PDFs to generate (for testing)')
    
    args = parser.parse_args()
    
    index_path = Path(args.index)
    if not index_path.is_absolute():
        index_path = LEGAL_OUTPUT_DIR / index_path
    
    generator = ExhibitGenerator()
    summary = generator.generate_exhibits_from_index(index_path, limit=args.limit)
    
    if 'error' in summary:
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nERROR: {e}")
        sys.exit(1)
