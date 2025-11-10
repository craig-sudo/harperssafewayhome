#!/usr/bin/env python3
"""
Harper's Master Control System - Unified Evidence Processing Interface
Complete control center for all evidence processing operations
Case: FDSJ-739-24 - Master Control System
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import logging
import time

class MasterControlSystem:
    """Master control system for all Harper's evidence processing operations."""
    
    def __init__(self):
        """Initialize the master control system."""
        self.setup_logging()
        
        # Available systems and their information
        self.systems = {
            '1': {
                'name': 'Intelligent Processing Manager',
                'script': 'intelligent_processing_manager.py',
                'description': 'AI-powered system that analyzes evidence and selects optimal processing',
                'icon': '🧠',
                'category': 'automatic'
            },
            '2': {
                'name': 'Enhanced Quality Processor',
                'script': 'enhanced_quality_processor.py',
                'description': 'Advanced OCR with quality control and smart categorization',
                'icon': '🔍',
                'category': 'processing'
            },
            '3': {
                'name': 'Secure Evidence Processor',
                'script': 'secure_evidence_processor.py',
                'description': 'Password-protected processor with professional export features',
                'icon': '🔐',
                'category': 'processing'
            },
            '4': {
                'name': 'Advanced Evidence Processor',
                'script': 'advanced_evidence_processor.py',
                'description': 'Multi-format processor for PDFs, videos, audio, and documents',
                'icon': '📄',
                'category': 'processing'
            },
            '5': {
                'name': 'Batch OCR Processor',
                'script': 'batch_ocr_processor.py',
                'description': 'Fast batch processing for large volumes of images',
                'icon': '⚡',
                'category': 'processing'
            },
            '6': {
                'name': 'OCR Monitor',
                'script': 'ocr_monitor.py',
                'description': 'Monitors processing progress and auto-restarts if needed',
                'icon': '👀',
                'category': 'monitoring'
            },
            '7': {
                'name': 'Automated Maintenance System',
                'script': 'automated_maintenance_system.py',
                'description': 'System optimization, cleanup, and performance monitoring',
                'icon': '🔧',
                'category': 'maintenance'
            },
            '8': {
                'name': 'Duplicate File Manager',
                'script': 'duplicate_file_manager.py',
                'description': 'Advanced duplicate detection and safe removal with backup protection',
                'icon': '🗑️',
                'category': 'maintenance'
            },
            '9': {
                'name': 'Evidence Integrity Checker',
                'script': 'evidence_integrity_checker.py',
                'description': 'Comprehensive file validation, corruption detection, and legal compliance',
                'icon': '🛡️',
                'category': 'validation'
            },
            '10': {
                'name': 'Court Package Exporter',
                'script': 'court_package_exporter.py',
                'description': 'Professional evidence package creation for court submission',
                'icon': '⚖️',
                'category': 'export'
            },
            '11': {
                'name': 'Court Report Generator',
                'script': 'court_report_generator.py',
                'description': 'Generate professional court-ready reports and timelines',
                'icon': '📋',
                'category': 'reporting'
            },
            '12': {
                'name': 'Evidence Timeline Generator',
                'script': 'evidence_timeline_generator.py',
                'description': 'Create chronological timeline of evidence for court presentation',
                'icon': '📅',
                'category': 'reporting'
            },
            '13': {
                'name': 'Legal Triage & Output Suite',
                'script': 'legal_triage_suite.py',
                'description': 'Court-admissible exhibit generation with SHA256 verification and defensibility statements',
                'icon': '⚖️',
                'category': 'legal'
            }
        }
        
        # Quick actions
        self.quick_actions = {
            'a': ('Auto-Process All Evidence', 'intelligent_processing_manager.py'),
            'b': ('Run System Maintenance', 'automated_maintenance_system.py'),
            'c': ('Check System Status', self.check_system_status),
            'd': ('View Recent Results', self.view_recent_results),
            'x': ('Manage Duplicate Files', 'duplicate_file_manager.py')
        }
        
        print(self.get_welcome_banner())

    def setup_logging(self):
        """Setup master control logging."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"master_control_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def get_welcome_banner(self) -> str:
        """Generate welcome banner."""
        return f"""
╔══════════════════════════════════════════════════════════════════╗
║           👑 HARPER'S MASTER CONTROL SYSTEM 👑                  ║
║                                                                  ║
║  🎯 Unified Command Center for Evidence Processing              ║
║  🚀 Professional Legal Documentation System                     ║
║  ⚖️ Case: FDSJ-739-24 | Complete Processing Suite             ║
║                                                                  ║
║  📅 System Initialized: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                           ║
╚══════════════════════════════════════════════════════════════════╝
        """

    def check_system_availability(self) -> Dict:
        """Check availability of all systems."""
        availability = {}
        
        for system_id, system_info in self.systems.items():
            script_path = Path(system_info['script'])
            availability[system_id] = {
                'available': script_path.exists(),
                'path': str(script_path),
                'name': system_info['name']
            }
        
        return availability

    def display_main_menu(self):
        """Display the main menu with all available options."""
        print("\n" + "="*70)
        print("🎛️ MASTER CONTROL PANEL")
        print("="*70)
        
        # Group systems by category
        categories = {
            'automatic': [],
            'processing': [],
            'monitoring': [],
            'maintenance': [],
            'reporting': []
        }
        
        availability = self.check_system_availability()
        
        for system_id, system_info in self.systems.items():
            categories[system_info['category']].append((system_id, system_info, availability[system_id]['available']))
        
        # Display categories
        category_names = {
            'automatic': '🤖 AUTOMATIC PROCESSING',
            'processing': '🔄 MANUAL PROCESSING',
            'monitoring': '👀 MONITORING & CONTROL',
            'maintenance': '🔧 SYSTEM MAINTENANCE',
            'reporting': '📊 REPORTS & ANALYSIS'
        }
        
        for category, systems in categories.items():
            if systems:
                print(f"\n{category_names[category]}:")
                for system_id, system_info, available in systems:
                    status = "✅" if available else "❌"
                    print(f"  [{system_id}] {status} {system_info['icon']} {system_info['name']}")
                    print(f"      {system_info['description']}")
        
        print(f"\n🚀 QUICK ACTIONS:")
        for key, (name, _) in self.quick_actions.items():
            print(f"  [{key.upper()}] ⚡ {name}")
        
        print(f"\n[0] 🚪 Exit Master Control System")
        print("="*70)

    def run_system(self, script_name: str) -> bool:
        """Run a specific system script."""
        script_path = Path(script_name)
        
        if not script_path.exists():
            print(f"❌ System not available: {script_name}")
            return False
        
        print(f"\n🚀 LAUNCHING: {script_name}")
        print("-" * 50)
        
        try:
            # Log the launch
            self.logger.info(f"Launching system: {script_name}")
            
            # Run the script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=os.getcwd(),
                text=True
            )
            
            if result.returncode == 0:
                print(f"\n✅ {script_name} completed successfully!")
                self.logger.info(f"System completed successfully: {script_name}")
                return True
            else:
                print(f"\n⚠️ {script_name} completed with return code: {result.returncode}")
                self.logger.warning(f"System completed with issues: {script_name}")
                return False
                
        except KeyboardInterrupt:
            print(f"\n🛑 {script_name} interrupted by user")
            self.logger.info(f"System interrupted by user: {script_name}")
            return False
        except Exception as e:
            print(f"\n❌ Failed to run {script_name}: {e}")
            self.logger.error(f"Failed to run system {script_name}: {e}")
            return False

    def check_system_status(self):
        """Check and display system status."""
        print("\n🔍 SYSTEM STATUS CHECK")
        print("="*50)
        
        # Check directories
        directories = ['custody_screenshots_smart_renamed', 'output', 'logs', 'secure_backups']
        print("\n📁 DIRECTORY STATUS:")
        for directory in directories:
            path = Path(directory)
            if path.exists():
                if path.is_dir():
                    file_count = len(list(path.rglob("*"))) if path.exists() else 0
                    print(f"  ✅ {directory} ({file_count} items)")
                else:
                    print(f"  ⚠️ {directory} (exists but not a directory)")
            else:
                print(f"  ❌ {directory} (missing)")
        
        # Check recent processing results
        output_dir = Path("output")
        if output_dir.exists():
            recent_files = sorted(output_dir.glob("*.csv"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            if recent_files:
                print(f"\n📊 RECENT PROCESSING RESULTS:")
                for file in recent_files:
                    mod_time = datetime.fromtimestamp(file.stat().st_mtime)
                    file_size = file.stat().st_size
                    print(f"  📄 {file.name}")
                    print(f"     Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"     Size: {file_size / 1024:.1f} KB")
            else:
                print(f"\n📊 No recent processing results found")
        
        # Check system performance
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(os.getcwd())
            
            print(f"\n💻 SYSTEM PERFORMANCE:")
            print(f"  🖥️ CPU Usage: {cpu_percent}%")
            print(f"  🧠 Memory Usage: {memory.percent}%")
            print(f"  💾 Disk Usage: {disk.used / disk.total * 100:.1f}%")
            print(f"  📊 Available Memory: {memory.available / 1024**3:.1f} GB")
            
        except ImportError:
            print(f"\n💻 SYSTEM PERFORMANCE: (psutil not available)")
        except Exception as e:
            print(f"\n💻 SYSTEM PERFORMANCE: Error checking - {e}")
        
        print("="*50)

    def view_recent_results(self):
        """View recent processing results."""
        print("\n📊 RECENT PROCESSING RESULTS")
        print("="*50)
        
        output_dir = Path("output")
        if not output_dir.exists():
            print("📁 No output directory found")
            return
        
        # Get recent CSV files
        csv_files = sorted(output_dir.glob("*.csv"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not csv_files:
            print("📄 No CSV result files found")
            return
        
        print(f"Found {len(csv_files)} result files:\n")
        
        for i, file in enumerate(csv_files[:10], 1):  # Show last 10 files
            mod_time = datetime.fromtimestamp(file.stat().st_mtime)
            file_size = file.stat().st_size
            
            print(f"[{i}] 📄 {file.name}")
            print(f"    📅 {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    💾 {file_size / 1024:.1f} KB")
            
            # Try to get row count
            try:
                import csv
                with open(file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    row_count = sum(1 for row in reader) - 1  # Subtract header
                    print(f"    📊 {row_count} records")
            except:
                print(f"    📊 Unable to read record count")
            
            print()
        
        if len(csv_files) > 10:
            print(f"... and {len(csv_files) - 10} more files")
        
        print("="*50)

    def run_interactive_mode(self):
        """Run the interactive master control interface."""
        print("🎮 Entering interactive mode...")
        print("💡 TIP: Use Ctrl+C to return to menu at any time")
        
        while True:
            try:
                self.display_main_menu()
                
                choice = input("\n🎯 Select option: ").strip().lower()
                
                if choice == '0':
                    print("\n👋 Exiting Master Control System...")
                    break
                
                elif choice in self.systems:
                    system_info = self.systems[choice]
                    print(f"\n🚀 Selected: {system_info['name']}")
                    confirm = input("Proceed? (y/N): ").strip().lower()
                    
                    if confirm in ['y', 'yes']:
                        success = self.run_system(system_info['script'])
                        
                        if success:
                            print("\n✨ System completed successfully!")
                        else:
                            print("\n⚠️ System completed with issues - check logs for details")
                        
                        input("\nPress Enter to continue...")
                    else:
                        print("❌ Operation cancelled")
                
                elif choice in self.quick_actions:
                    action_name, action = self.quick_actions[choice]
                    print(f"\n⚡ Executing: {action_name}")
                    
                    if callable(action):
                        action()
                    else:
                        self.run_system(action)
                    
                    input("\nPress Enter to continue...")
                
                else:
                    print("❌ Invalid selection. Please try again.")
                    time.sleep(1)
            
            except KeyboardInterrupt:
                print("\n\n🔄 Returning to main menu...")
                continue
            except EOFError:
                print("\n\n👋 Exiting Master Control System...")
                break
            except Exception as e:
                print(f"\n❌ Error in interactive mode: {e}")
                self.logger.error(f"Interactive mode error: {e}")
                input("Press Enter to continue...")

    def run_batch_mode(self, operations: List[str]):
        """Run multiple operations in batch mode."""
        print(f"🔄 BATCH MODE: Running {len(operations)} operations")
        print("="*50)
        
        results = []
        
        for i, operation in enumerate(operations, 1):
            print(f"\n[{i}/{len(operations)}] Processing: {operation}")
            
            if operation in self.systems:
                system_info = self.systems[operation]
                success = self.run_system(system_info['script'])
                results.append((system_info['name'], success))
            elif operation in self.quick_actions:
                action_name, action = self.quick_actions[operation]
                try:
                    if callable(action):
                        action()
                        results.append((action_name, True))
                    else:
                        success = self.run_system(action)
                        results.append((action_name, success))
                except Exception as e:
                    print(f"❌ Quick action failed: {e}")
                    results.append((action_name, False))
            else:
                print(f"❌ Unknown operation: {operation}")
                results.append((operation, False))
        
        # Display batch results
        print("\n" + "="*50)
        print("📊 BATCH PROCESSING RESULTS")
        print("="*50)
        
        successful = 0
        for operation, success in results:
            status = "✅" if success else "❌"
            print(f"{status} {operation}")
            if success:
                successful += 1
        
        print(f"\n📈 Success Rate: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
        print("="*50)

def main():
    """Main entry point for master control system."""
    try:
        # Check for help flag first
        if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
            print("Harper's Master Control System - Unified Evidence Processing")
            print("Usage: python master_control_system.py")
            print("Interactive menu system for all evidence processing tools")
            return
        
        master_control = MasterControlSystem()
        
        # Check command line arguments for batch mode
        if len(sys.argv) > 1:
            # Batch mode
            operations = sys.argv[1:]
            master_control.run_batch_mode(operations)
        else:
            # Interactive mode
            master_control.run_interactive_mode()
    
    except KeyboardInterrupt:
        print("\n\n🛑 Master Control System terminated by user")
    except Exception as e:
        print(f"\n❌ Critical error in Master Control System: {e}")
        logging.error(f"Critical error: {e}")

if __name__ == "__main__":
    main()