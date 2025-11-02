#!/usr/bin/env python3
"""
Harper's Duplicate File Manager - Advanced Duplicate Detection & Removal
Safe duplicate management with backup and verification for evidence files
Case: FDSJ-739-24 - Duplicate File Management System
"""

import os
import hashlib
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
import sqlite3
from utils.path_utils import ensure_long_path

class DuplicateFileManager:
    """Advanced duplicate file detection and management system."""
    
    def __init__(self):
        """Initialize the duplicate file manager."""
        self.evidence_dirs = [
            Path("custody_screenshots_smart_renamed"),
            Path("custody_screenshots_organized"),
            Path("custody_screenshots")
        ]
        
        self.output_dir = Path("output")
        self.backup_dir = Path("duplicate_backups")
        self.reports_dir = Path("duplicate_reports")
        
        # Ensure directories exist
        for directory in [self.backup_dir, self.reports_dir]:
            directory.mkdir(exist_ok=True)
        
        # Setup logging first
        self.setup_logging()
        
        # Initialize database for duplicate tracking
        self.init_duplicate_database()
        
        # Processing statistics
        self.stats = {
            'total_checked': 0,
            'duplicates_found': 0,
            'duplicates_deleted': 0,
            'space_freed': 0,
            'backup_created': 0
        }
        
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║           🔍 HARPER'S DUPLICATE FILE MANAGER 🔍                  ║
║                                                                  ║
║  🎯 Advanced Duplicate Detection & Safe Removal                 ║
║  🛡️ Backup Protection & Verification System                    ║
║  📊 Comprehensive Analysis & Reporting                          ║
║                                                                  ║
║  📋 Case: FDSJ-739-24                                          ║
║  ⚠️ LEGAL EVIDENCE - SAFE PROCESSING ONLY                      ║
╚══════════════════════════════════════════════════════════════════╝
        """)

    def setup_logging(self):
        """Setup logging system for duplicate management."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"duplicate_manager_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def init_duplicate_database(self):
        """Initialize SQLite database for duplicate tracking."""
        db_path = self.reports_dir / 'duplicates.db'
        
        try:
            self.conn = sqlite3.connect(db_path)
            cursor = self.conn.cursor()
            
            # Create duplicate files table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS duplicate_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_hash TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    file_modified TEXT NOT NULL,
                    first_seen TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    backup_path TEXT,
                    deleted_date TEXT
                )
            ''')
            
            # Create duplicate groups table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS duplicate_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_hash TEXT NOT NULL,
                    file_count INTEGER NOT NULL,
                    total_size INTEGER NOT NULL,
                    keeper_file TEXT,
                    deleted_files INTEGER DEFAULT 0,
                    space_saved INTEGER DEFAULT 0,
                    processing_date TEXT NOT NULL
                )
            ''')
            
            self.conn.commit()
            self.logger.info("Duplicate tracking database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize duplicate database: {e}")

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file for duplicate detection."""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return None

    def scan_for_duplicates(self) -> Dict:
        """Comprehensive scan for duplicate files across all evidence directories."""
        print("🔍 SCANNING FOR DUPLICATE FILES...")
        self.logger.info("Starting comprehensive duplicate scan")
        
        file_hashes = {}
        scan_results = {
            'total_files': 0,
            'unique_files': 0,
            'duplicate_groups': 0,
            'total_duplicates': 0,
            'potential_space_savings': 0,
            'duplicate_details': []
        }
        
        # Supported file extensions
        supported_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', 
                              '.pdf', '.doc', '.docx', '.txt', '.mp4', '.avi', '.mov'}
        
        try:
            # Scan all evidence directories
            for evidence_dir in self.evidence_dirs:
                if not evidence_dir.exists():
                    continue
                
                print(f"📂 Scanning: {evidence_dir}")
                
                for file_path in evidence_dir.rglob("*"):
                    if not file_path.is_file():
                        continue
                    
                    # Check if file type is supported
                    if file_path.suffix.lower() not in supported_extensions:
                        continue
                    
                    scan_results['total_files'] += 1
                    self.stats['total_checked'] += 1
                    
                    try:
                        # Calculate file hash
                        file_hash = self.calculate_file_hash(file_path)
                        if not file_hash:
                            continue
                        
                        file_info = {
                            'path': file_path,
                            'size': file_path.stat().st_size,
                            'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
                        }
                        
                        if file_hash in file_hashes:
                            # Duplicate found
                            file_hashes[file_hash].append(file_info)
                        else:
                            # First occurrence
                            file_hashes[file_hash] = [file_info]
                            scan_results['unique_files'] += 1
                        
                        # Store in database
                        self.store_file_info(file_hash, file_path, file_info)
                        
                    except Exception as e:
                        self.logger.error(f"Error processing file {file_path}: {e}")
                        continue
            
            # Process duplicate groups
            for file_hash, file_list in file_hashes.items():
                if len(file_list) > 1:
                    # Found duplicates
                    scan_results['duplicate_groups'] += 1
                    scan_results['total_duplicates'] += len(file_list) - 1
                    
                    # Calculate potential space savings (all but one file)
                    file_size = file_list[0]['size']
                    space_savings = file_size * (len(file_list) - 1)
                    scan_results['potential_space_savings'] += space_savings
                    
                    # Sort by modification date (keep newest) or path (for consistency)
                    file_list.sort(key=lambda x: (x['modified'], str(x['path'])), reverse=True)
                    
                    duplicate_group = {
                        'hash': file_hash,
                        'file_count': len(file_list),
                        'file_size': file_size,
                        'space_savings': space_savings,
                        'keeper_file': str(file_list[0]['path']),  # Keep the newest/first
                        'duplicate_files': [str(f['path']) for f in file_list[1:]]
                    }
                    
                    scan_results['duplicate_details'].append(duplicate_group)
                    self.stats['duplicates_found'] += len(file_list) - 1
            
            # Save scan results
            self.save_scan_results(scan_results)
            
            print(f"✅ SCAN COMPLETE!")
            print(f"📊 Total Files: {scan_results['total_files']:,}")
            print(f"🔍 Unique Files: {scan_results['unique_files']:,}")
            print(f"📦 Duplicate Groups: {scan_results['duplicate_groups']:,}")
            print(f"🗂️ Total Duplicates: {scan_results['total_duplicates']:,}")
            print(f"💾 Potential Space Savings: {scan_results['potential_space_savings'] / 1024 / 1024:.1f} MB")
            
            return scan_results
            
        except Exception as e:
            self.logger.error(f"Duplicate scan failed: {e}")
            return scan_results

    def store_file_info(self, file_hash: str, file_path: Path, file_info: Dict):
        """Store file information in the database."""
        try:
            cursor = self.conn.cursor()
            
            # Check if file already exists in database
            cursor.execute('SELECT id FROM duplicate_files WHERE file_path = ?', (str(file_path),))
            if cursor.fetchone():
                return  # Already exists
            
            # Insert new file record
            cursor.execute('''
                INSERT INTO duplicate_files 
                (file_hash, file_path, file_size, file_modified, first_seen)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                file_hash,
                str(file_path),
                file_info['size'],
                file_info['modified'].isoformat(),
                datetime.now().isoformat()
            ))
            
            self.conn.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to store file info for {file_path}: {e}")

    def save_scan_results(self, results: Dict):
        """Save scan results to JSON file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = self.reports_dir / f"duplicate_scan_{timestamp}.json"
            
            # Convert Path objects to strings for JSON serialization
            json_results = json.loads(json.dumps(results, default=str))
            
            with open(ensure_long_path(results_file), 'w', encoding='utf-8') as f:
                json.dump(json_results, f, indent=2, ensure_ascii=False)
            
            print(f"📋 Scan results saved: {results_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save scan results: {e}")

    def create_backup(self, file_path: Path) -> Optional[Path]:
        """Create backup of file before deletion."""
        try:
            # Create timestamped backup directory
            backup_subdir = self.backup_dir / datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_subdir.mkdir(exist_ok=True)
            
            # Preserve directory structure
            relative_path = file_path.relative_to(file_path.anchor)
            backup_path = backup_subdir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file to backup location
            from utils.path_utils import ensure_long_path as _elp
            shutil.copy2(_elp(file_path), _elp(backup_path))
            
            self.stats['backup_created'] += 1
            self.logger.info(f"Backup created: {backup_path}")
            
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Failed to create backup for {file_path}: {e}")
            return None

    def safe_delete_duplicates(self, scan_results: Dict, confirm_each: bool = True) -> Dict:
        """Safely delete duplicate files with backup protection."""
        print("\n🗑️ SAFE DUPLICATE DELETION PROCESS")
        print("=" * 50)
        
        if not scan_results.get('duplicate_details'):
            print("ℹ️ No duplicates found to delete")
            return {'deleted': 0, 'failed': 0, 'skipped': 0}
        
        deletion_results = {
            'deleted': 0,
            'failed': 0,
            'skipped': 0,
            'space_freed': 0,
            'backups_created': 0
        }
        
        print(f"⚠️ Found {len(scan_results['duplicate_details'])} duplicate groups")
        print(f"📊 Potential space savings: {scan_results['potential_space_savings'] / 1024 / 1024:.1f} MB")
        
        if confirm_each:
            proceed = input("\n🤔 Do you want to proceed with deletion? (y/N): ").strip().lower()
            if proceed not in ['y', 'yes']:
                print("❌ Deletion cancelled by user")
                return deletion_results
        
        try:
            for group_idx, duplicate_group in enumerate(scan_results['duplicate_details'], 1):
                print(f"\n📦 Processing Group {group_idx}/{len(scan_results['duplicate_details'])}")
                print(f"🔍 Hash: {duplicate_group['hash'][:16]}...")
                print(f"📁 Keeper: {Path(duplicate_group['keeper_file']).name}")
                print(f"🗂️ Duplicates to delete: {len(duplicate_group['duplicate_files'])}")
                
                if confirm_each:
                    show_details = input("📋 Show detailed file list? (y/N): ").strip().lower()
                    if show_details in ['y', 'yes']:
                        print("📁 Files in this group:")
                        print(f"   ✅ KEEP: {duplicate_group['keeper_file']}")
                        for dup_file in duplicate_group['duplicate_files']:
                            print(f"   🗑️ DELETE: {dup_file}")
                    
                    confirm = input(f"🗑️ Delete {len(duplicate_group['duplicate_files'])} duplicates? (y/N/s to skip): ").strip().lower()
                    if confirm == 's':
                        deletion_results['skipped'] += len(duplicate_group['duplicate_files'])
                        continue
                    elif confirm not in ['y', 'yes']:
                        deletion_results['skipped'] += len(duplicate_group['duplicate_files'])
                        continue
                
                # Process duplicates in this group
                group_deleted = 0
                group_space_freed = 0
                
                for dup_file_str in duplicate_group['duplicate_files']:
                    dup_file_path = Path(dup_file_str)
                    
                    if not dup_file_path.exists():
                        self.logger.warning(f"File not found: {dup_file_path}")
                        deletion_results['failed'] += 1
                        continue
                    
                    try:
                        # Create backup before deletion
                        backup_path = self.create_backup(dup_file_path)
                        if not backup_path:
                            self.logger.error(f"Backup failed for {dup_file_path}, skipping deletion")
                            deletion_results['failed'] += 1
                            continue
                        
                        # Delete the duplicate file
                        file_size = dup_file_path.stat().st_size
                        dup_file_path.unlink()
                        
                        # Update database
                        self.update_file_status(str(dup_file_path), 'deleted', str(backup_path))
                        
                        # Update statistics
                        deletion_results['deleted'] += 1
                        group_deleted += 1
                        deletion_results['space_freed'] += file_size
                        group_space_freed += file_size
                        self.stats['duplicates_deleted'] += 1
                        self.stats['space_freed'] += file_size
                        
                        self.logger.info(f"Deleted duplicate: {dup_file_path}")
                        
                    except Exception as e:
                        self.logger.error(f"Failed to delete {dup_file_path}: {e}")
                        deletion_results['failed'] += 1
                
                print(f"✅ Group {group_idx}: Deleted {group_deleted} files, freed {group_space_freed / 1024:.1f} KB")
                
                # Store group results in database
                self.store_group_results(duplicate_group, group_deleted, group_space_freed)
            
            # Final summary
            print(f"\n🎉 DELETION COMPLETE!")
            print(f"✅ Deleted: {deletion_results['deleted']} files")
            print(f"❌ Failed: {deletion_results['failed']} files")
            print(f"⏭️ Skipped: {deletion_results['skipped']} files")
            print(f"💾 Space Freed: {deletion_results['space_freed'] / 1024 / 1024:.1f} MB")
            print(f"🛡️ Backups Created: {self.stats['backup_created']}")
            
            return deletion_results
            
        except Exception as e:
            self.logger.error(f"Deletion process failed: {e}")
            return deletion_results

    def update_file_status(self, file_path: str, status: str, backup_path: str = None):
        """Update file status in the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE duplicate_files 
                SET status = ?, backup_path = ?, deleted_date = ?
                WHERE file_path = ?
            ''', (status, backup_path, datetime.now().isoformat(), file_path))
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to update file status: {e}")

    def store_group_results(self, duplicate_group: Dict, deleted_count: int, space_saved: int):
        """Store duplicate group processing results."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO duplicate_groups 
                (group_hash, file_count, total_size, keeper_file, deleted_files, space_saved, processing_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                duplicate_group['hash'],
                duplicate_group['file_count'],
                duplicate_group['file_size'],
                duplicate_group['keeper_file'],
                deleted_count,
                space_saved,
                datetime.now().isoformat()
            ))
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to store group results: {e}")

    def restore_from_backup(self, backup_date: str = None):
        """Restore files from backup if needed."""
        print("🔄 BACKUP RESTORATION SYSTEM")
        print("=" * 40)
        
        if not self.backup_dir.exists():
            print("❌ No backup directory found")
            return
        
        # List available backups
        backup_dirs = [d for d in self.backup_dir.iterdir() if d.is_dir()]
        if not backup_dirs:
            print("❌ No backups found")
            return
        
        backup_dirs.sort(reverse=True)  # Newest first
        
        print("📁 Available backups:")
        for i, backup_dir in enumerate(backup_dirs, 1):
            file_count = len(list(backup_dir.rglob("*")))
            print(f"  [{i}] {backup_dir.name} ({file_count} files)")
        
        try:
            choice = input("\n🔄 Select backup to restore (number or 'all'): ").strip()
            
            if choice.lower() == 'all':
                selected_backups = backup_dirs
            else:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(backup_dirs):
                    selected_backups = [backup_dirs[choice_idx]]
                else:
                    print("❌ Invalid selection")
                    return
            
            restored_count = 0
            for backup_dir in selected_backups:
                print(f"\n🔄 Restoring from: {backup_dir.name}")
                
                for backup_file in backup_dir.rglob("*"):
                    if not backup_file.is_file():
                        continue
                    
                    # Determine original location
                    relative_path = backup_file.relative_to(backup_dir)
                    original_path = Path(relative_path.anchor) / relative_path
                    
                    try:
                        # Create directory if needed
                        original_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Restore file
                        from utils.path_utils import ensure_long_path as _elp
                        shutil.copy2(_elp(backup_file), _elp(original_path))
                        restored_count += 1
                        
                        # Update database
                        self.update_file_status(str(original_path), 'restored')
                        
                        print(f"✅ Restored: {original_path.name}")
                        
                    except Exception as e:
                        self.logger.error(f"Failed to restore {backup_file}: {e}")
            
            print(f"\n🎉 Restoration complete! Restored {restored_count} files")
            
        except (ValueError, KeyboardInterrupt):
            print("❌ Restoration cancelled")

    def generate_report(self) -> Dict:
        """Generate comprehensive duplicate management report."""
        print("📊 GENERATING DUPLICATE MANAGEMENT REPORT...")
        
        try:
            # Get database statistics
            cursor = self.conn.cursor()
            
            # Count total files tracked
            cursor.execute('SELECT COUNT(*) FROM duplicate_files')
            total_tracked = cursor.fetchone()[0]
            
            # Count deleted files
            cursor.execute('SELECT COUNT(*) FROM duplicate_files WHERE status = "deleted"')
            total_deleted = cursor.fetchone()[0]
            
            # Count duplicate groups processed
            cursor.execute('SELECT COUNT(*), SUM(space_saved) FROM duplicate_groups')
            groups_processed, total_space_saved = cursor.fetchone()
            
            # Recent activity
            cursor.execute('''
                SELECT COUNT(*) FROM duplicate_files 
                WHERE first_seen >= datetime('now', '-7 days')
            ''')
            recent_files = cursor.fetchone()[0]
            
            report = {
                'report_timestamp': datetime.now().isoformat(),
                'session_statistics': {
                    'files_checked': self.stats['total_checked'],
                    'duplicates_found': self.stats['duplicates_found'],
                    'duplicates_deleted': self.stats['duplicates_deleted'],
                    'space_freed_bytes': self.stats['space_freed'],
                    'space_freed_mb': self.stats['space_freed'] / 1024 / 1024,
                    'backups_created': self.stats['backup_created']
                },
                'database_statistics': {
                    'total_files_tracked': total_tracked,
                    'total_files_deleted': total_deleted,
                    'duplicate_groups_processed': groups_processed or 0,
                    'total_space_saved_bytes': total_space_saved or 0,
                    'total_space_saved_mb': (total_space_saved or 0) / 1024 / 1024,
                    'recent_files_7days': recent_files
                },
                'system_health': {
                    'backup_directory_exists': self.backup_dir.exists(),
                    'database_accessible': True,
                    'evidence_directories': [str(d) for d in self.evidence_dirs if d.exists()]
                }
            }
            
            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.reports_dir / f"duplicate_management_report_{timestamp}.json"
            
            with open(ensure_long_path(report_file), 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"📋 Report saved: {report_file}")
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            return {'error': str(e)}

    def interactive_menu(self):
        """Interactive menu for duplicate management."""
        while True:
            print("\n" + "="*60)
            print("🔍 DUPLICATE FILE MANAGEMENT MENU")
            print("="*60)
            print("[1] 🔍 Scan for Duplicates")
            print("[2] 🗑️ Delete Duplicates (Safe)")
            print("[3] 🔄 Restore from Backup")
            print("[4] 📊 Generate Report")
            print("[5] 📋 View Statistics")
            print("[0] 🚪 Exit")
            print("="*60)
            
            try:
                choice = input("🎯 Select option: ").strip()
                
                if choice == '1':
                    scan_results = self.scan_for_duplicates()
                    if scan_results['total_duplicates'] > 0:
                        proceed = input("\n🗑️ Delete duplicates now? (y/N): ").strip().lower()
                        if proceed in ['y', 'yes']:
                            self.safe_delete_duplicates(scan_results)
                
                elif choice == '2':
                    # Load latest scan results
                    latest_scan = self.load_latest_scan_results()
                    if latest_scan:
                        self.safe_delete_duplicates(latest_scan)
                    else:
                        print("❌ No scan results found. Please run scan first.")
                
                elif choice == '3':
                    self.restore_from_backup()
                
                elif choice == '4':
                    self.generate_report()
                
                elif choice == '5':
                    self.show_statistics()
                
                elif choice == '0':
                    print("👋 Exiting Duplicate File Manager")
                    break
                
                else:
                    print("❌ Invalid option. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting Duplicate File Manager")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def load_latest_scan_results(self) -> Optional[Dict]:
        """Load the most recent scan results."""
        try:
            scan_files = list(self.reports_dir.glob("duplicate_scan_*.json"))
            if not scan_files:
                return None
            
            latest_file = max(scan_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Failed to load scan results: {e}")
            return None

    def show_statistics(self):
        """Display current statistics."""
        print("\n📊 DUPLICATE MANAGEMENT STATISTICS")
        print("="*50)
        print(f"📁 Files Checked: {self.stats['total_checked']:,}")
        print(f"🔍 Duplicates Found: {self.stats['duplicates_found']:,}")
        print(f"🗑️ Duplicates Deleted: {self.stats['duplicates_deleted']:,}")
        print(f"💾 Space Freed: {self.stats['space_freed'] / 1024 / 1024:.1f} MB")
        print(f"🛡️ Backups Created: {self.stats['backup_created']:,}")
        print("="*50)

    def __del__(self):
        """Cleanup database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()


def main():
    """Main execution function."""
    try:
        # Check for help flag first
        import sys
        if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
            print("Harper's Duplicate File Manager - Advanced Duplicate Detection")
            print("Usage: python duplicate_file_manager.py [mode]")
            print("Modes:")
            print("  scan     - Quick duplicate scan")
            print("  clean    - Safe duplicate removal")
            print("  restore  - Restore from backup")
            print("  (no args) - Interactive mode")
            return
        
        duplicate_manager = DuplicateFileManager()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            mode = sys.argv[1].lower()
            
            if mode == 'scan':
                scan_results = duplicate_manager.scan_for_duplicates()
                duplicate_manager.generate_report()
            elif mode == 'delete':
                scan_results = duplicate_manager.scan_for_duplicates()
                if scan_results['total_duplicates'] > 0:
                    duplicate_manager.safe_delete_duplicates(scan_results, confirm_each=False)
            elif mode == 'report':
                duplicate_manager.generate_report()
            else:
                print("❌ Invalid mode. Use: scan, delete, or report")
        else:
            # Interactive mode
            duplicate_manager.interactive_menu()
    
    except KeyboardInterrupt:
        print("\n👋 Duplicate File Manager terminated by user")
    except Exception as e:
        print(f"❌ Critical error in Duplicate File Manager: {e}")
        logging.error(f"Critical error: {e}")


if __name__ == "__main__":
    main()