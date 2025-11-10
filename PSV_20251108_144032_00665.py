#!/usr/bin/env python3
"""
Harper's Automated Maintenance & Optimization System
Keeps the evidence processing system optimized and maintains data integrity
Case: FDSJ-739-24 - System Maintenance & Optimization
"""

import os
import sys
import shutil
import json
import csv
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import hashlib
import subprocess
import psutil
import time

class AutomatedMaintenanceSystem:
    """Automated system maintenance and optimization for Harper's evidence processing."""
    
    def __init__(self):
        """Initialize the maintenance system."""
        self.setup_logging()
        
        # Maintenance configuration
        self.config = {
            'max_log_age_days': 30,
            'max_backup_count': 10,
            'max_output_age_days': 90,
            'disk_space_threshold': 0.85,  # 85% full
            'duplicate_detection': True,
            'performance_monitoring': True,
            'auto_cleanup': True
        }
        
        # System paths
        self.paths = {
            'logs': Path('logs'),
            'output': Path('output'),
            'backups': Path('secure_backups'),
            'reports': Path('reports'),
            'temp': Path('temp'),
            'maintenance': Path('maintenance_reports')
        }
        
        # Ensure all directories exist
        for path in self.paths.values():
            path.mkdir(exist_ok=True)
        
        # Initialize maintenance database
        self.init_maintenance_db()
        
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║     🔧 HARPER'S AUTOMATED MAINTENANCE SYSTEM 🔧                 ║
║                                                                  ║
║  🧹 Automated Cleanup & Optimization                           ║
║  📊 Performance Monitoring & Reporting                         ║
║  🛡️ Data Integrity & Backup Management                        ║
║                                                                  ║
║  📋 Case: FDSJ-739-24                                          ║
║  🤖 Intelligent System Maintenance                             ║
╚══════════════════════════════════════════════════════════════════╝
        """)

    def setup_logging(self):
        """Setup maintenance logging system."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"maintenance_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def init_maintenance_db(self):
        """Initialize SQLite database for maintenance tracking."""
        db_path = self.paths['maintenance'] / 'maintenance.db'
        
        try:
            self.conn = sqlite3.connect(db_path)
            cursor = self.conn.cursor()
            
            # Create maintenance log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS maintenance_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    files_affected INTEGER DEFAULT 0,
                    space_freed INTEGER DEFAULT 0,
                    duration_seconds REAL DEFAULT 0,
                    details TEXT
                )
            ''')
            
            # Create file integrity table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_integrity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filepath TEXT UNIQUE NOT NULL,
                    file_hash TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    last_verified TEXT NOT NULL,
                    status TEXT DEFAULT 'verified'
                )
            ''')
            
            # Create performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage REAL,
                    active_processes INTEGER,
                    processing_speed REAL
                )
            ''')
            
            self.conn.commit()
            self.logger.info("Maintenance database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize maintenance database: {e}")

    def log_maintenance_task(self, task_type: str, description: str, status: str, 
                           files_affected: int = 0, space_freed: int = 0, 
                           duration: float = 0, details: str = ""):
        """Log maintenance task to database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO maintenance_log 
                (timestamp, task_type, description, status, files_affected, space_freed, duration_seconds, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), task_type, description, status, 
                  files_affected, space_freed, duration, details))
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to log maintenance task: {e}")

    def check_disk_space(self) -> Dict:
        """Check available disk space and usage."""
        try:
            total, used, free = shutil.disk_usage(os.getcwd())
            usage_percent = used / total
            
            disk_info = {
                'total_gb': total / (1024**3),
                'used_gb': used / (1024**3),
                'free_gb': free / (1024**3),
                'usage_percent': usage_percent,
                'needs_cleanup': usage_percent > self.config['disk_space_threshold']
            }
            
            if disk_info['needs_cleanup']:
                self.logger.warning(f"Disk usage high: {usage_percent:.1%}")
            
            return disk_info
            
        except Exception as e:
            self.logger.error(f"Failed to check disk space: {e}")
            return {}

    def cleanup_old_logs(self) -> Tuple[int, int]:
        """Clean up old log files."""
        print("🧹 CLEANING UP OLD LOG FILES...")
        start_time = time.time()
        
        files_removed = 0
        space_freed = 0
        cutoff_date = datetime.now() - timedelta(days=self.config['max_log_age_days'])
        
        try:
            for log_file in self.paths['logs'].glob('*.log'):
                try:
                    file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        file_size = log_file.stat().st_size
                        log_file.unlink()
                        files_removed += 1
                        space_freed += file_size
                        self.logger.info(f"Removed old log: {log_file.name}")
                except Exception as e:
                    self.logger.error(f"Failed to remove log {log_file}: {e}")
            
            duration = time.time() - start_time
            
            self.log_maintenance_task(
                'cleanup_logs', 
                f'Cleaned up logs older than {self.config["max_log_age_days"]} days',
                'completed',
                files_removed,
                space_freed,
                duration
            )
            
            print(f"   ✅ Removed {files_removed} log files, freed {space_freed / 1024:.1f} KB")
            return files_removed, space_freed
            
        except Exception as e:
            self.logger.error(f"Log cleanup failed: {e}")
            self.log_maintenance_task('cleanup_logs', 'Log cleanup failed', 'failed', 0, 0, 0, str(e))
            return 0, 0

    def manage_backups(self) -> Tuple[int, int]:
        """Manage backup files - keep only recent ones."""
        print("🛡️ MANAGING BACKUP FILES...")
        start_time = time.time()
        
        files_removed = 0
        space_freed = 0
        
        try:
            # Get all backup files sorted by modification time
            backup_files = []
            for backup_file in self.paths['backups'].glob('*.csv'):
                backup_files.append((backup_file, backup_file.stat().st_mtime))
            
            backup_files.sort(key=lambda x: x[1], reverse=True)  # Newest first
            
            # Keep only the most recent backups
            if len(backup_files) > self.config['max_backup_count']:
                files_to_remove = backup_files[self.config['max_backup_count']:]
                
                for backup_file, _ in files_to_remove:
                    try:
                        file_size = backup_file.stat().st_size
                        backup_file.unlink()
                        files_removed += 1
                        space_freed += file_size
                        self.logger.info(f"Removed old backup: {backup_file.name}")
                    except Exception as e:
                        self.logger.error(f"Failed to remove backup {backup_file}: {e}")
            
            duration = time.time() - start_time
            
            self.log_maintenance_task(
                'manage_backups',
                f'Maintained backup count at {self.config["max_backup_count"]} files',
                'completed',
                files_removed,
                space_freed,
                duration
            )
            
            print(f"   ✅ Managed backups: kept {min(len(backup_files), self.config['max_backup_count'])}, removed {files_removed}")
            return files_removed, space_freed
            
        except Exception as e:
            self.logger.error(f"Backup management failed: {e}")
            self.log_maintenance_task('manage_backups', 'Backup management failed', 'failed', 0, 0, 0, str(e))
            return 0, 0

    def verify_file_integrity(self) -> Dict:
        """Verify integrity of important files."""
        print("🔍 VERIFYING FILE INTEGRITY...")
        start_time = time.time()
        
        integrity_report = {
            'total_files': 0,
            'verified': 0,
            'modified': 0,
            'corrupted': 0,
            'missing': 0
        }
        
        try:
            # Check output files
            for output_file in self.paths['output'].glob('*.csv'):
                integrity_report['total_files'] += 1
                
                try:
                    # Calculate current hash
                    current_hash = self.calculate_file_hash(output_file)
                    file_size = output_file.stat().st_size
                    
                    # Check if file is in database
                    cursor = self.conn.cursor()
                    cursor.execute('''
                        SELECT file_hash, file_size FROM file_integrity 
                        WHERE filepath = ?
                    ''', (str(output_file),))
                    
                    result = cursor.fetchone()
                    
                    if result is None:
                        # New file - add to database
                        cursor.execute('''
                            INSERT INTO file_integrity (filepath, file_hash, file_size, last_verified)
                            VALUES (?, ?, ?, ?)
                        ''', (str(output_file), current_hash, file_size, datetime.now().isoformat()))
                        integrity_report['verified'] += 1
                    else:
                        stored_hash, stored_size = result
                        if current_hash == stored_hash and file_size == stored_size:
                            # File unchanged
                            cursor.execute('''
                                UPDATE file_integrity 
                                SET last_verified = ? WHERE filepath = ?
                            ''', (datetime.now().isoformat(), str(output_file)))
                            integrity_report['verified'] += 1
                        else:
                            # File modified
                            cursor.execute('''
                                UPDATE file_integrity 
                                SET file_hash = ?, file_size = ?, last_verified = ?, status = ?
                                WHERE filepath = ?
                            ''', (current_hash, file_size, datetime.now().isoformat(), 'modified', str(output_file)))
                            integrity_report['modified'] += 1
                            self.logger.warning(f"File modified: {output_file.name}")
                    
                    self.conn.commit()
                    
                except Exception as e:
                    integrity_report['corrupted'] += 1
                    self.logger.error(f"Integrity check failed for {output_file}: {e}")
            
            duration = time.time() - start_time
            
            self.log_maintenance_task(
                'verify_integrity',
                f'Verified integrity of {integrity_report["total_files"]} files',
                'completed',
                integrity_report['total_files'],
                0,
                duration,
                json.dumps(integrity_report)
            )
            
            print(f"   ✅ Verified: {integrity_report['verified']}, Modified: {integrity_report['modified']}, Issues: {integrity_report['corrupted']}")
            return integrity_report
            
        except Exception as e:
            self.logger.error(f"File integrity verification failed: {e}")
            return integrity_report

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""

    def detect_duplicates(self) -> Dict:
        """Detect and report duplicate files."""
        print("🔍 DETECTING DUPLICATE FILES...")
        start_time = time.time()
        
        duplicates_report = {
            'total_checked': 0,
            'duplicates_found': 0,
            'space_wasted': 0,
            'duplicate_groups': []
        }
        
        try:
            # Check evidence files for duplicates
            file_hashes = {}
            evidence_dir = Path("custody_screenshots_smart_renamed")
            
            if evidence_dir.exists():
                for file_path in evidence_dir.rglob("*"):
                    if file_path.is_file() and file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                        duplicates_report['total_checked'] += 1
                        
                        try:
                            file_hash = self.calculate_file_hash(file_path)
                            if file_hash in file_hashes:
                                # Duplicate found
                                file_hashes[file_hash].append(file_path)
                            else:
                                file_hashes[file_hash] = [file_path]
                        except Exception as e:
                            self.logger.error(f"Failed to hash file {file_path}: {e}")
            
            # Process duplicates
            for file_hash, file_list in file_hashes.items():
                if len(file_list) > 1:
                    duplicates_report['duplicates_found'] += len(file_list) - 1
                    
                    # Calculate wasted space (all but one file)
                    file_size = file_list[0].stat().st_size
                    duplicates_report['space_wasted'] += file_size * (len(file_list) - 1)
                    
                    duplicates_report['duplicate_groups'].append({
                        'hash': file_hash,
                        'count': len(file_list),
                        'size': file_size,
                        'files': [str(f) for f in file_list]
                    })
            
            duration = time.time() - start_time
            
            self.log_maintenance_task(
                'detect_duplicates',
                f'Found {duplicates_report["duplicates_found"]} duplicate files',
                'completed',
                duplicates_report['total_checked'],
                0,
                duration,
                json.dumps(duplicates_report, default=str)
            )
            
            print(f"   ✅ Checked {duplicates_report['total_checked']} files, found {duplicates_report['duplicates_found']} duplicates")
            if duplicates_report['space_wasted'] > 0:
                print(f"   💾 Potential space savings: {duplicates_report['space_wasted'] / 1024 / 1024:.1f} MB")
            
            return duplicates_report
            
        except Exception as e:
            self.logger.error(f"Duplicate detection failed: {e}")
            return duplicates_report

    def monitor_system_performance(self) -> Dict:
        """Monitor system performance metrics."""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(os.getcwd())
            
            performance_data = {
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': cpu_usage,
                'memory_usage': memory.percent,
                'disk_usage': (disk.used / disk.total) * 100,
                'available_memory_gb': memory.available / (1024**3),
                'processes': len(psutil.pids())
            }
            
            # Store in database
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO performance_metrics 
                (timestamp, cpu_usage, memory_usage, disk_usage, active_processes)
                VALUES (?, ?, ?, ?, ?)
            ''', (performance_data['timestamp'], performance_data['cpu_usage'],
                  performance_data['memory_usage'], performance_data['disk_usage'],
                  performance_data['processes']))
            self.conn.commit()
            
            return performance_data
            
        except Exception as e:
            self.logger.error(f"Performance monitoring failed: {e}")
            return {}

    def optimize_csv_files(self) -> Tuple[int, int]:
        """Optimize CSV files by removing empty rows and compressing."""
        print("📊 OPTIMIZING CSV FILES...")
        start_time = time.time()
        
        files_optimized = 0
        space_saved = 0
        
        try:
            for csv_file in self.paths['output'].glob('*.csv'):
                try:
                    original_size = csv_file.stat().st_size
                    
                    # Read and clean CSV
                    clean_rows = []
                    with open(csv_file, 'r', encoding='utf-8', newline='') as f:
                        reader = csv.reader(f)
                        headers = next(reader, None)
                        if headers:
                            clean_rows.append(headers)
                            
                            for row in reader:
                                # Skip empty rows or rows with only empty cells
                                if any(cell.strip() for cell in row):
                                    clean_rows.append(row)
                    
                    # Write back optimized data
                    if len(clean_rows) > 1:  # At least headers + 1 data row
                        temp_file = csv_file.with_suffix('.tmp')
                        with open(temp_file, 'w', encoding='utf-8', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerows(clean_rows)
                        
                        # Replace original file
                        temp_file.replace(csv_file)
                        
                        new_size = csv_file.stat().st_size
                        space_saved += original_size - new_size
                        files_optimized += 1
                        
                        if original_size != new_size:
                            self.logger.info(f"Optimized {csv_file.name}: {original_size} -> {new_size} bytes")
                    
                except Exception as e:
                    self.logger.error(f"Failed to optimize {csv_file}: {e}")
            
            duration = time.time() - start_time
            
            self.log_maintenance_task(
                'optimize_csv',
                f'Optimized {files_optimized} CSV files',
                'completed',
                files_optimized,
                space_saved,
                duration
            )
            
            print(f"   ✅ Optimized {files_optimized} CSV files, saved {space_saved / 1024:.1f} KB")
            return files_optimized, space_saved
            
        except Exception as e:
            self.logger.error(f"CSV optimization failed: {e}")
            return 0, 0

    def generate_maintenance_report(self) -> Dict:
        """Generate comprehensive maintenance report."""
        print("📋 GENERATING MAINTENANCE REPORT...")
        
        try:
            # Get recent maintenance activities
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT task_type, COUNT(*) as count, SUM(files_affected) as total_files,
                       SUM(space_freed) as total_space_freed, AVG(duration_seconds) as avg_duration
                FROM maintenance_log 
                WHERE timestamp >= datetime('now', '-7 days')
                GROUP BY task_type
            ''')
            
            maintenance_summary = {}
            for row in cursor.fetchall():
                task_type, count, total_files, total_space_freed, avg_duration = row
                maintenance_summary[task_type] = {
                    'executions': count,
                    'files_affected': total_files or 0,
                    'space_freed': total_space_freed or 0,
                    'avg_duration': avg_duration or 0
                }
            
            # Get performance trends
            cursor.execute('''
                SELECT AVG(cpu_usage), AVG(memory_usage), AVG(disk_usage)
                FROM performance_metrics 
                WHERE timestamp >= datetime('now', '-7 days')
            ''')
            
            perf_avg = cursor.fetchone()
            performance_summary = {
                'avg_cpu_usage': perf_avg[0] if perf_avg[0] else 0,
                'avg_memory_usage': perf_avg[1] if perf_avg[1] else 0,
                'avg_disk_usage': perf_avg[2] if perf_avg[2] else 0
            }
            
            # System status
            disk_info = self.check_disk_space()
            current_performance = self.monitor_system_performance()
            
            report = {
                'report_timestamp': datetime.now().isoformat(),
                'system_status': {
                    'disk_space': disk_info,
                    'current_performance': current_performance,
                    'health_status': 'good' if not disk_info.get('needs_cleanup', False) else 'attention_needed'
                },
                'maintenance_summary': maintenance_summary,
                'performance_trends': performance_summary,
                'recommendations': []
            }
            
            # Generate recommendations
            if disk_info.get('usage_percent', 0) > 0.8:
                report['recommendations'].append("Disk usage is high - consider cleanup")
            
            if performance_summary.get('avg_cpu_usage', 0) > 80:
                report['recommendations'].append("High CPU usage detected - monitor processing loads")
            
            if performance_summary.get('avg_memory_usage', 0) > 80:
                report['recommendations'].append("High memory usage - consider batch size optimization")
            
            # Save report
            report_file = self.paths['maintenance'] / f"maintenance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Maintenance report saved: {report_file}")
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate maintenance report: {e}")
            return {}

    def run_full_maintenance(self):
        """Run complete maintenance cycle."""
        print("🔧 STARTING FULL MAINTENANCE CYCLE...")
        start_time = time.time()
        
        maintenance_results = {
            'start_time': datetime.now().isoformat(),
            'tasks_completed': [],
            'total_files_affected': 0,
            'total_space_freed': 0,
            'errors': []
        }
        
        try:
            # Task 1: Clean up old logs
            try:
                files_removed, space_freed = self.cleanup_old_logs()
                maintenance_results['tasks_completed'].append('cleanup_logs')
                maintenance_results['total_files_affected'] += files_removed
                maintenance_results['total_space_freed'] += space_freed
            except Exception as e:
                maintenance_results['errors'].append(f"Log cleanup failed: {e}")
            
            # Task 2: Manage backups
            try:
                files_removed, space_freed = self.manage_backups()
                maintenance_results['tasks_completed'].append('manage_backups')
                maintenance_results['total_files_affected'] += files_removed
                maintenance_results['total_space_freed'] += space_freed
            except Exception as e:
                maintenance_results['errors'].append(f"Backup management failed: {e}")
            
            # Task 3: Verify file integrity
            try:
                integrity_report = self.verify_file_integrity()
                maintenance_results['tasks_completed'].append('verify_integrity')
                maintenance_results['file_integrity'] = integrity_report
            except Exception as e:
                maintenance_results['errors'].append(f"Integrity verification failed: {e}")
            
            # Task 4: Detect duplicates
            try:
                duplicates_report = self.detect_duplicates()
                maintenance_results['tasks_completed'].append('detect_duplicates')
                maintenance_results['duplicates'] = duplicates_report
            except Exception as e:
                maintenance_results['errors'].append(f"Duplicate detection failed: {e}")
            
            # Task 5: Optimize CSV files
            try:
                files_optimized, space_saved = self.optimize_csv_files()
                maintenance_results['tasks_completed'].append('optimize_csv')
                maintenance_results['total_files_affected'] += files_optimized
                maintenance_results['total_space_freed'] += space_saved
            except Exception as e:
                maintenance_results['errors'].append(f"CSV optimization failed: {e}")
            
            # Task 6: Monitor performance
            try:
                performance_data = self.monitor_system_performance()
                maintenance_results['tasks_completed'].append('monitor_performance')
                maintenance_results['performance'] = performance_data
            except Exception as e:
                maintenance_results['errors'].append(f"Performance monitoring failed: {e}")
            
            # Task 7: Generate report
            try:
                report = self.generate_maintenance_report()
                maintenance_results['tasks_completed'].append('generate_report')
                maintenance_results['maintenance_report'] = report
            except Exception as e:
                maintenance_results['errors'].append(f"Report generation failed: {e}")
            
            # Finalize
            total_duration = time.time() - start_time
            maintenance_results['end_time'] = datetime.now().isoformat()
            maintenance_results['total_duration'] = total_duration
            
            # Log overall maintenance
            self.log_maintenance_task(
                'full_maintenance',
                'Complete maintenance cycle',
                'completed' if not maintenance_results['errors'] else 'completed_with_errors',
                maintenance_results['total_files_affected'],
                maintenance_results['total_space_freed'],
                total_duration,
                json.dumps(maintenance_results, default=str)
            )
            
            # Display summary
            print("\n" + "="*70)
            print("🎉 MAINTENANCE CYCLE COMPLETED")
            print("="*70)
            print(f"⏱️ Duration: {total_duration:.1f} seconds")
            print(f"📁 Files Affected: {maintenance_results['total_files_affected']}")
            print(f"💾 Space Freed: {maintenance_results['total_space_freed'] / 1024:.1f} KB")
            print(f"✅ Tasks Completed: {len(maintenance_results['tasks_completed'])}")
            
            if maintenance_results['errors']:
                print(f"⚠️ Errors: {len(maintenance_results['errors'])}")
                for error in maintenance_results['errors']:
                    print(f"   • {error}")
            
            print("="*70)
            
        except Exception as e:
            self.logger.error(f"Full maintenance cycle failed: {e}")
            print(f"❌ Maintenance cycle failed: {e}")

    def __del__(self):
        """Cleanup database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    """Main maintenance execution."""
    try:
        maintenance_system = AutomatedMaintenanceSystem()
        maintenance_system.run_full_maintenance()
        
    except KeyboardInterrupt:
        print("\n🛑 Maintenance interrupted by user")
    except Exception as e:
        print(f"❌ Critical maintenance error: {e}")

if __name__ == "__main__":
    main()