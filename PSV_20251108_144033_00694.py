#!/usr/bin/env python3
"""
Harper's Intelligent Processing Manager
Smart system that automatically selects the best processing method based on evidence analysis
Case: FDSJ-739-24 - Intelligent Evidence Processing System
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import shutil
import logging

class IntelligentProcessingManager:
    """Intelligent manager that analyzes evidence and selects optimal processing methods."""
    
    def __init__(self):
        """Initialize the intelligent processing manager."""
        self.base_dir = Path("custody_screenshots_smart_renamed")
        self.setup_logging()
        
        # Available processors
        self.processors = {
            'enhanced_quality': {
                'script': 'enhanced_quality_processor.py',
                'description': 'Enhanced OCR with quality control and smart categorization',
                'best_for': ['screenshots', 'text_messages', 'social_media'],
                'min_files': 10
            },
            'secure_evidence': {
                'script': 'secure_evidence_processor.py',
                'description': 'Secure processor with password protection and export features',
                'best_for': ['sensitive_documents', 'court_evidence'],
                'min_files': 1
            },
            'advanced_evidence': {
                'script': 'advanced_evidence_processor.py',
                'description': 'Multi-format processor for PDFs, videos, audio, and documents',
                'best_for': ['mixed_formats', 'multimedia_evidence'],
                'min_files': 1
            },
            'batch_ocr': {
                'script': 'batch_ocr_processor.py',
                'description': 'Fast batch processing for large volumes of images',
                'best_for': ['large_batches', 'simple_images'],
                'min_files': 50
            }
        }
        
        self.evidence_analysis = {}
        
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║       🧠 HARPER'S INTELLIGENT PROCESSING MANAGER 🧠             ║
║                                                                  ║
║  🔍 Analyzes Evidence Types & Selects Optimal Processing        ║
║  🎯 Smart Routing to Best Available Processor                   ║
║  📊 Comprehensive Analysis & Recommendations                    ║
║                                                                  ║
║  📋 Case: FDSJ-739-24                                          ║
║  🤖 AI-Powered Processing Selection                             ║
╚══════════════════════════════════════════════════════════════════╝
        """)

    def setup_logging(self):
        """Setup logging system."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"intelligent_manager_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def analyze_evidence_structure(self) -> Dict:
        """Analyze the evidence directory structure and content types."""
        print("🔍 ANALYZING EVIDENCE STRUCTURE...")
        
        analysis = {
            'total_files': 0,
            'file_types': {},
            'directories': {},
            'size_analysis': {
                'small_files': 0,  # < 100KB
                'medium_files': 0,  # 100KB - 1MB
                'large_files': 0   # > 1MB
            },
            'estimated_complexity': 'unknown'
        }
        
        if not self.base_dir.exists():
            print(f"⚠️ Evidence directory not found: {self.base_dir}")
            return analysis
        
        # Analyze directory structure
        for item in self.base_dir.rglob("*"):
            if item.is_file():
                analysis['total_files'] += 1
                
                # File type analysis
                ext = item.suffix.lower()
                analysis['file_types'][ext] = analysis['file_types'].get(ext, 0) + 1
                
                # Directory categorization
                relative_path = item.relative_to(self.base_dir)
                category = str(relative_path.parts[0]) if relative_path.parts else 'root'
                analysis['directories'][category] = analysis['directories'].get(category, 0) + 1
                
                # Size analysis
                try:
                    file_size = item.stat().st_size
                    if file_size < 100 * 1024:  # 100KB
                        analysis['size_analysis']['small_files'] += 1
                    elif file_size < 1024 * 1024:  # 1MB
                        analysis['size_analysis']['medium_files'] += 1
                    else:
                        analysis['size_analysis']['large_files'] += 1
                except:
                    pass
        
        # Determine complexity
        if analysis['total_files'] > 1000:
            analysis['estimated_complexity'] = 'high'
        elif analysis['total_files'] > 100:
            analysis['estimated_complexity'] = 'medium'
        else:
            analysis['estimated_complexity'] = 'low'
        
        return analysis

    def identify_evidence_types(self, analysis: Dict) -> List[str]:
        """Identify the types of evidence based on directory structure and file analysis."""
        evidence_types = []
        
        # Check directories for evidence types
        directory_mapping = {
            'conversations': 'text_messages',
            'threatening': 'threatening_messages',
            'custody_violation': 'custody_documents',
            'financial': 'financial_documents',
            'legal_court': 'court_documents',
            'medical': 'medical_records',
            'school': 'school_communications'
        }
        
        for directory, evidence_type in directory_mapping.items():
            if any(directory in dir_name.lower() for dir_name in analysis['directories'].keys()):
                evidence_types.append(evidence_type)
        
        # Check file types for multimedia evidence
        multimedia_extensions = {'.mp4', '.avi', '.mov', '.mp3', '.wav', '.pdf', '.docx', '.doc'}
        if any(ext in multimedia_extensions for ext in analysis['file_types'].keys()):
            evidence_types.append('multimedia_evidence')
        
        # Check for screenshot evidence
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
        if any(ext in image_extensions for ext in analysis['file_types'].keys()):
            evidence_types.append('screenshots')
        
        # Default to general if no specific types identified
        if not evidence_types:
            evidence_types.append('general_documents')
        
        return evidence_types

    def recommend_processor(self, analysis: Dict, evidence_types: List[str]) -> Tuple[str, str]:
        """Recommend the best processor based on analysis."""
        print("🎯 ANALYZING OPTIMAL PROCESSING METHOD...")
        
        scores = {}
        
        # Score each processor
        for processor_name, processor_info in self.processors.items():
            score = 0
            
            # Check if minimum file requirement is met
            if analysis['total_files'] >= processor_info['min_files']:
                score += 10
            else:
                score -= 5
            
            # Score based on evidence type match
            for evidence_type in evidence_types:
                if any(best_type in evidence_type for best_type in processor_info['best_for']):
                    score += 20
            
            # Complexity-based scoring
            if processor_name == 'enhanced_quality' and analysis['estimated_complexity'] in ['medium', 'high']:
                score += 15
            elif processor_name == 'batch_ocr' and analysis['estimated_complexity'] == 'high':
                score += 10
            elif processor_name == 'advanced_evidence' and 'multimedia_evidence' in evidence_types:
                score += 25
            elif processor_name == 'secure_evidence':
                score += 5  # Always a good backup option
            
            scores[processor_name] = score
        
        # Select the best processor
        best_processor = max(scores.items(), key=lambda x: x[1])
        
        recommendation_reason = f"Selected based on {analysis['total_files']} files, complexity: {analysis['estimated_complexity']}, types: {', '.join(evidence_types)}"
        
        return best_processor[0], recommendation_reason

    def check_processor_availability(self, processor_name: str) -> bool:
        """Check if the recommended processor is available."""
        script_path = Path(self.processors[processor_name]['script'])
        return script_path.exists()

    def display_analysis_report(self, analysis: Dict, evidence_types: List[str], 
                              recommended_processor: str, reason: str):
        """Display comprehensive analysis report."""
        print("\n" + "="*70)
        print("📊 EVIDENCE ANALYSIS REPORT")
        print("="*70)
        
        print(f"📁 Total Files Found: {analysis['total_files']}")
        print(f"🗂️ Complexity Level: {analysis['estimated_complexity'].upper()}")
        
        print(f"\n📂 Directory Structure:")
        for directory, count in sorted(analysis['directories'].items()):
            print(f"   • {directory}: {count} files")
        
        print(f"\n📄 File Types:")
        for file_type, count in sorted(analysis['file_types'].items()):
            if file_type:  # Skip empty extensions
                print(f"   • {file_type}: {count} files")
        
        print(f"\n🔍 Evidence Types Detected:")
        for evidence_type in evidence_types:
            print(f"   • {evidence_type.replace('_', ' ').title()}")
        
        print(f"\n🎯 RECOMMENDED PROCESSOR: {recommended_processor.upper()}")
        print(f"📝 Description: {self.processors[recommended_processor]['description']}")
        print(f"💡 Reason: {reason}")
        
        print("="*70)

    def run_processor(self, processor_name: str) -> bool:
        """Run the selected processor."""
        script_path = self.processors[processor_name]['script']
        
        print(f"\n🚀 LAUNCHING {processor_name.upper()} PROCESSOR...")
        print(f"📜 Script: {script_path}")
        
        try:
            # Run the processor
            result = subprocess.run(
                [sys.executable, script_path],
                cwd=os.getcwd(),
                capture_output=False,  # Allow real-time output
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ {processor_name.upper()} completed successfully!")
                return True
            else:
                print(f"❌ {processor_name.upper()} failed with return code: {result.returncode}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to run {processor_name}: {e}")
            self.logger.error(f"Failed to run processor {processor_name}: {e}")
            return False

    def create_processing_report(self, analysis: Dict, processor_used: str, success: bool):
        """Create a comprehensive processing report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'evidence_analysis': analysis,
            'processor_used': processor_used,
            'processor_description': self.processors[processor_used]['description'],
            'processing_success': success,
            'recommendations': []
        }
        
        # Add recommendations based on results
        if not success:
            report['recommendations'].append("Processing failed - consider manual intervention")
            report['recommendations'].append("Check logs for detailed error information")
        
        if analysis['total_files'] > 500:
            report['recommendations'].append("Large dataset detected - consider batch processing")
        
        if len(analysis['file_types']) > 5:
            report['recommendations'].append("Multiple file types detected - verify all were processed correctly")
        
        # Save report
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f"processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"📊 Processing report saved: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save processing report: {e}")

    def interactive_processor_selection(self) -> str:
        """Allow user to manually select processor if desired."""
        print("\n🤔 Would you like to use a different processor?")
        print("Available options:")
        
        for i, (name, info) in enumerate(self.processors.items(), 1):
            available = "✅" if self.check_processor_availability(name) else "❌"
            print(f"  {i}. {available} {name.replace('_', ' ').title()}")
            print(f"     {info['description']}")
        
        print(f"  {len(self.processors) + 1}. Continue with recommendation")
        
        try:
            choice = input("\nEnter your choice (or press Enter for recommendation): ").strip()
            
            if not choice or choice == str(len(self.processors) + 1):
                return None  # Use recommendation
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(self.processors):
                processor_name = list(self.processors.keys())[choice_idx]
                if self.check_processor_availability(processor_name):
                    return processor_name
                else:
                    print("❌ Selected processor is not available")
                    return None
            else:
                print("❌ Invalid choice")
                return None
                
        except (ValueError, KeyboardInterrupt):
            return None

    def main_processing_flow(self):
        """Main intelligent processing flow."""
        try:
            # Step 1: Analyze evidence
            print("🔍 STEP 1: ANALYZING EVIDENCE...")
            analysis = self.analyze_evidence_structure()
            
            if analysis['total_files'] == 0:
                print("⚠️ No files found for processing")
                return
            
            # Step 2: Identify evidence types
            print("🔍 STEP 2: IDENTIFYING EVIDENCE TYPES...")
            evidence_types = self.identify_evidence_types(analysis)
            
            # Step 3: Recommend processor
            print("🔍 STEP 3: SELECTING OPTIMAL PROCESSOR...")
            recommended_processor, reason = self.recommend_processor(analysis, evidence_types)
            
            # Step 4: Display analysis
            self.display_analysis_report(analysis, evidence_types, recommended_processor, reason)
            
            # Step 5: Check availability
            if not self.check_processor_availability(recommended_processor):
                print(f"❌ Recommended processor '{recommended_processor}' is not available!")
                
                # Find alternative
                available_processors = [name for name in self.processors.keys() 
                                      if self.check_processor_availability(name)]
                
                if available_processors:
                    recommended_processor = available_processors[0]
                    print(f"🔄 Using alternative processor: {recommended_processor}")
                else:
                    print("❌ No processors are available!")
                    return
            
            # Step 6: User confirmation or manual selection
            user_choice = self.interactive_processor_selection()
            if user_choice:
                recommended_processor = user_choice
                print(f"👤 User selected: {recommended_processor}")
            
            # Step 7: Run processor
            print(f"\n🚀 EXECUTING PROCESSING PIPELINE...")
            success = self.run_processor(recommended_processor)
            
            # Step 8: Generate report
            self.create_processing_report(analysis, recommended_processor, success)
            
            if success:
                print("\n🎉 INTELLIGENT PROCESSING COMPLETED SUCCESSFULLY!")
                print("📁 Check the 'output' directory for results")
                print("📊 Check the 'reports' directory for detailed analysis")
            else:
                print("\n⚠️ Processing completed with issues")
                print("📋 Check logs for troubleshooting information")
                
        except KeyboardInterrupt:
            print("\n🛑 Processing interrupted by user")
        except Exception as e:
            print(f"❌ Critical error in processing flow: {e}")
            self.logger.error(f"Critical error: {e}")

def main():
    """Main entry point."""
    manager = IntelligentProcessingManager()
    manager.main_processing_flow()

if __name__ == "__main__":
    main()