#!/usr/bin/env python3
"""
Harper's Ultimate Progress Monitor - Real-Time Processing Dashboard
Comprehensive monitoring system for all evidence processing activities
Case: FDSJ-739-24 - Advanced Progress Tracking & Analytics
"""

import time
import os
import csv
import threading
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging
import psutil
import sys

class UltimateProgressMonitor:
    """Advanced real-time monitoring system for all evidence processing activities."""
    
    def __init__(self):
        """Initialize the ultimate progress monitor."""
        self.output_folder = Path("output")
        self.evidence_folder = Path("custody_screenshots_smart_renamed")
        self.logs_folder = Path("logs")
        self.reports_folder = Path("reports")
        
        # Ensure directories exist
        for folder in [self.output_folder, self.logs_folder, self.reports_folder]:
            folder.mkdir(exist_ok=True)
        
        # Initialize database for progress tracking
        self.init_progress_database()
        
        # Monitoring configuration
        self.monitor_config = {
            'refresh_interval': 5,  # seconds
            'history_retention_days': 30,
            'alert_thresholds': {
                'processing_stall': 300,  # 5 minutes
                'error_rate': 0.1,        # 10%
                'memory_usage': 0.8       # 80%
            }
        }
        
        # Statistics tracking
        self.stats = {
            'session_start': datetime.now(),
            'total_processed': 0,
            'processing_rate': 0.0,
            'error_count': 0,
            'alerts': []
        }
        
        # Setup logging
        self.setup_logging()
        
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║        📊 HARPER'S ULTIMATE PROGRESS MONITOR 📊                 ║
║                                                                  ║
║  🎯 Real-Time Processing Dashboard & Analytics                  ║
║  📈 Comprehensive Progress Tracking System                      ║
║  🚨 Intelligent Alerting & Performance Monitoring              ║
║                                                                  ║
║  📋 Case: FDSJ-739-24                                          ║
║  ⏰ Monitor Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                           ║
╚══════════════════════════════════════════════════════════════════╝
        """)
    
    def setup_logging(self):
        """Setup comprehensive logging system."""
        log_file = self.logs_folder / f"ultimate_progress_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def init_progress_database(self):
        """Initialize SQLite database for progress tracking."""
        db_path = self.reports_folder / 'progress_tracking.db'
        
        try:
            self.conn = sqlite3.connect(db_path)
            cursor = self.conn.cursor()
            
            # Create progress snapshots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS progress_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    processor_type TEXT NOT NULL,
                    files_processed INTEGER DEFAULT 0,
                    files_failed INTEGER DEFAULT 0,
                    processing_rate REAL DEFAULT 0,
                    memory_usage REAL DEFAULT 0,
                    cpu_usage REAL DEFAULT 0,
                    disk_usage REAL DEFAULT 0,
                    active_processes INTEGER DEFAULT 0,
                    quality_metrics TEXT,
                    notes TEXT
                )
            ''')
            
            # Create alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    resolved INTEGER DEFAULT 0
                )
            ''')
            
            self.conn.commit()
            self.logger.info("Progress tracking database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize progress database: {e}")

    def log_message(self, message, level='INFO'):
        """Enhanced logging with levels."""
        if level == 'INFO':
            self.logger.info(message)
        elif level == 'WARNING':
            self.logger.warning(message)
        elif level == 'ERROR':
            self.logger.error(message)
        elif level == 'DEBUG':
            self.logger.debug(message)
    
    def get_system_metrics(self) -> Dict:
        """Get current system performance metrics."""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(os.getcwd())
            
            return {
                'cpu_usage': cpu_usage,
                'memory_usage': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_usage': (disk.used / disk.total) * 100,
                'disk_free_gb': disk.free / (1024**3),
                'active_processes': len(psutil.pids()),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            return {}

    def analyze_processing_files(self) -> Dict:
        """Analyze all processing output files for comprehensive status."""
        analysis = {
            'ocr_processing': {},
            'enhanced_processing': {},
            'secure_processing': {},
            'advanced_processing': {},
            'total_files': 0,
            'total_records': 0,
            'latest_activity': None
        }
        
        try:
            # Analyze different types of output files
            file_patterns = {
                'ocr_processing': 'harper_ocr_results_*.csv',
                'enhanced_processing': 'harper_enhanced_results_*.csv',
                'secure_processing': 'harper_evidence_*.csv',
                'advanced_processing': 'advanced_evidence_results_*.csv'
            }
            
            all_files = []
            
            for process_type, pattern in file_patterns.items():
                files = list(self.output_folder.glob(pattern))
                analysis[process_type] = {
                    'file_count': len(files),
                    'total_records': 0,
                    'latest_file': None,
                    'size_mb': 0
                }
                
                if files:
                    # Find latest file
                    latest_file = max(files, key=os.path.getmtime)
                    analysis[process_type]['latest_file'] = {
                        'name': latest_file.name,
                        'modified': datetime.fromtimestamp(latest_file.stat().st_mtime),
                        'size': latest_file.stat().st_size
                    }
                    
                    all_files.append((latest_file, latest_file.stat().st_mtime))
                    
                    # Count records and calculate total size
                    total_records = 0
                    total_size = 0
                    
                    for file in files:
                        try:
                            with open(file, 'r', encoding='utf-8') as f:
                                record_count = sum(1 for line in f) - 1  # Subtract header
                                total_records += record_count
                                total_size += file.stat().st_size
                        except Exception as e:
                            self.logger.warning(f"Could not read file {file}: {e}")
                    
                    analysis[process_type]['total_records'] = total_records
                    analysis[process_type]['size_mb'] = total_size / (1024 * 1024)
                    
                    analysis['total_records'] += total_records
                
                analysis['total_files'] += len(files)
            
            # Find latest activity across all files
            if all_files:
                latest_file, latest_time = max(all_files, key=lambda x: x[1])
                analysis['latest_activity'] = {
                    'file': latest_file.name,
                    'timestamp': datetime.fromtimestamp(latest_time),
                    'minutes_ago': (datetime.now() - datetime.fromtimestamp(latest_time)).total_seconds() / 60
                }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze processing files: {e}")
            return analysis

    def count_evidence_files(self) -> Dict:
        """Count total evidence files available for processing."""
        try:
            if not self.evidence_folder.exists():
                return {'total': 0, 'by_type': {}, 'error': 'Evidence folder not found'}
            
            file_counts = {
                'images': 0,
                'documents': 0,
                'videos': 0,
                'audio': 0,
                'other': 0
            }
            
            # File type categorization
            image_exts = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
            doc_exts = {'.pdf', '.doc', '.docx', '.txt', '.rtf'}
            video_exts = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv'}
            audio_exts = {'.mp3', '.wav', '.m4a', '.ogg', '.flac'}
            
            total_files = 0
            for file_path in self.evidence_folder.rglob("*"):
                if file_path.is_file():
                    total_files += 1
                    ext = file_path.suffix.lower()
                    
                    if ext in image_exts:
                        file_counts['images'] += 1
                    elif ext in doc_exts:
                        file_counts['documents'] += 1
                    elif ext in video_exts:
                        file_counts['videos'] += 1
                    elif ext in audio_exts:
                        file_counts['audio'] += 1
                    else:
                        file_counts['other'] += 1
            
            return {
                'total': total_files,
                'by_type': file_counts,
                'processing_potential': {
                    'ocr_ready': file_counts['images'],
                    'advanced_processing': file_counts['documents'] + file_counts['videos'] + file_counts['audio']
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to count evidence files: {e}")
            return {'total': 0, 'by_type': {}, 'error': str(e)}

    def check_processing_health(self) -> Dict:
        """Check the health status of processing systems."""
        health_status = {
            'overall_status': 'unknown',
            'issues': [],
            'recommendations': [],
            'last_activity_minutes': None,
            'processing_rate': 0.0,
            'error_indicators': []
        }
        
        try:
            # Check for recent activity
            analysis = self.analyze_processing_files()
            if analysis['latest_activity']:
                minutes_ago = analysis['latest_activity']['minutes_ago']
                health_status['last_activity_minutes'] = minutes_ago
                
                if minutes_ago > self.monitor_config['alert_thresholds']['processing_stall']:
                    health_status['issues'].append(f"No processing activity for {minutes_ago:.0f} minutes")
                    health_status['recommendations'].append("Check if processing systems are running")
            
            # Calculate processing rate
            if analysis['total_records'] > 0:
                session_duration = (datetime.now() - self.stats['session_start']).total_seconds() / 3600  # hours
                if session_duration > 0:
                    health_status['processing_rate'] = analysis['total_records'] / session_duration
            
            # Check system resources
            system_metrics = self.get_system_metrics()
            if system_metrics:
                if system_metrics['memory_usage'] > (self.monitor_config['alert_thresholds']['memory_usage'] * 100):
                    health_status['issues'].append(f"High memory usage: {system_metrics['memory_usage']:.1f}%")
                    health_status['recommendations'].append("Consider reducing batch sizes or restarting processes")
                
                if system_metrics['disk_usage'] > 90:
                    health_status['issues'].append(f"Low disk space: {system_metrics['disk_usage']:.1f}% used")
                    health_status['recommendations'].append("Clean up old files or add more storage")
            
            # Check for error patterns in logs
            error_patterns = self.scan_recent_logs_for_errors()
            if error_patterns:
                health_status['error_indicators'].extend(error_patterns)
            
            # Determine overall status
            if not health_status['issues'] and not health_status['error_indicators']:
                health_status['overall_status'] = 'healthy'
            elif len(health_status['issues']) <= 2:
                health_status['overall_status'] = 'warning'
            else:
                health_status['overall_status'] = 'critical'
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            health_status['overall_status'] = 'error'
            health_status['issues'].append(f"Health check failed: {e}")
            return health_status

    def scan_recent_logs_for_errors(self) -> List[str]:
        """Scan recent log files for error patterns."""
        error_patterns = []
        
        try:
            # Get recent log files
            recent_logs = []
            cutoff_time = datetime.now() - timedelta(hours=1)  # Last hour
            
            for log_file in self.logs_folder.glob("*.log"):
                if datetime.fromtimestamp(log_file.stat().st_mtime) > cutoff_time:
                    recent_logs.append(log_file)
            
            # Scan for error patterns
            error_keywords = ['ERROR', 'FAILED', 'EXCEPTION', 'CRITICAL', 'CRASHED']
            
            for log_file in recent_logs:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        error_count = 0
                        
                        for line in lines:
                            if any(keyword in line.upper() for keyword in error_keywords):
                                error_count += 1
                        
                        if error_count > 0:
                            error_patterns.append(f"{log_file.name}: {error_count} errors found")
                            
                except Exception as e:
                    self.logger.debug(f"Could not scan log file {log_file}: {e}")
            
            return error_patterns
            
        except Exception as e:
            self.logger.error(f"Failed to scan logs for errors: {e}")
            return []

    def record_progress_snapshot(self, processor_type: str = "monitor"):
        """Record a progress snapshot to the database."""
        try:
            # Get current metrics
            system_metrics = self.get_system_metrics()
            analysis = self.analyze_processing_files()
            
            # Calculate processing statistics
            processing_rate = 0.0
            if analysis['total_records'] > 0:
                session_duration = (datetime.now() - self.stats['session_start']).total_seconds() / 3600
                if session_duration > 0:
                    processing_rate = analysis['total_records'] / session_duration
            
            # Quality metrics (placeholder for future enhancement)
            quality_metrics = json.dumps({
                'total_files': analysis['total_files'],
                'total_records': analysis['total_records'],
                'file_types': list(analysis.keys())
            })
            
            # Insert snapshot
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO progress_snapshots 
                (timestamp, processor_type, files_processed, processing_rate, 
                 memory_usage, cpu_usage, disk_usage, active_processes, quality_metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                processor_type,
                analysis['total_records'],
                processing_rate,
                system_metrics.get('memory_usage', 0),
                system_metrics.get('cpu_usage', 0),
                system_metrics.get('disk_usage', 0),
                system_metrics.get('active_processes', 0),
                quality_metrics
            ))
            
            self.conn.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to record progress snapshot: {e}")

    def create_alert(self, alert_type: str, severity: str, message: str):
        """Create an alert in the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO alerts (timestamp, alert_type, severity, message)
                VALUES (?, ?, ?, ?)
            ''', (datetime.now().isoformat(), alert_type, severity, message))
            
            self.conn.commit()
            
            # Add to current session alerts
            self.stats['alerts'].append({
                'timestamp': datetime.now(),
                'type': alert_type,
                'severity': severity,
                'message': message
            })
            
            self.log_message(f"ALERT [{severity}] {alert_type}: {message}", 'WARNING')
            
        except Exception as e:
            self.logger.error(f"Failed to create alert: {e}")

    def check_all_processing(self):
        """Comprehensive check of all processing systems with enhanced analytics."""
        self.log_message("Starting comprehensive processing check...")
        
        try:
            # Get all analysis data
            system_metrics = self.get_system_metrics()
            file_analysis = self.analyze_processing_files()
            evidence_count = self.count_evidence_files()
            health_status = self.check_processing_health()
            
            # Record progress snapshot
            self.record_progress_snapshot()
            
            # Check for alerts
            if health_status['overall_status'] == 'critical':
                self.create_alert('system_health', 'HIGH', 'Critical system health issues detected')
            elif health_status['overall_status'] == 'warning':
                self.create_alert('system_health', 'MEDIUM', 'System health warnings detected')
            
            # Compile comprehensive results
            results = {
                'timestamp': datetime.now().isoformat(),
                'system_metrics': system_metrics,
                'file_analysis': file_analysis,
                'evidence_inventory': evidence_count,
                'health_status': health_status,
                'session_stats': {
                    'session_duration_minutes': (datetime.now() - self.stats['session_start']).total_seconds() / 60,
                    'monitoring_cycles': getattr(self, 'monitoring_cycles', 0) + 1
                }
            }
            
            # Update session stats
            if not hasattr(self, 'monitoring_cycles'):
                self.monitoring_cycles = 0
            self.monitoring_cycles += 1
            
            return results
            
        except Exception as e:
            self.logger.error(f"Comprehensive processing check failed: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}

    def display_comprehensive_dashboard(self, results: Dict):
        """Display comprehensive real-time dashboard."""
        # Clear screen for real-time updates
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║        📊 HARPER'S REAL-TIME PROCESSING DASHBOARD 📊            ║
║                                                                  ║
║  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Case: FDSJ-739-24                        ║
║  ⏱️ Session: {results.get('session_stats', {}).get('session_duration_minutes', 0):.0f} min | Cycles: {results.get('session_stats', {}).get('monitoring_cycles', 0)}              ║
╚══════════════════════════════════════════════════════════════════╝
        """)
        
        # System Health Status
        health = results.get('health_status', {})
        status_icon = {
            'healthy': '🟢',
            'warning': '🟡', 
            'critical': '🔴',
            'error': '⚫',
            'unknown': '⚪'
        }.get(health.get('overall_status', 'unknown'), '⚪')
        
        print(f"🏥 SYSTEM HEALTH: {status_icon} {health.get('overall_status', 'unknown').upper()}")
        
        if health.get('issues'):
            print("⚠️ Issues Detected:")
            for issue in health['issues'][:3]:  # Show top 3 issues
                print(f"   • {issue}")
        
        if health.get('recommendations'):
            print("💡 Recommendations:")
            for rec in health['recommendations'][:2]:  # Show top 2 recommendations
                print(f"   • {rec}")
        
        print()
        
        # Processing Progress
        print("📊 PROCESSING PROGRESS:")
        file_analysis = results.get('file_analysis', {})
        
        processing_types = [
            ('OCR Processing', 'ocr_processing', '🔍'),
            ('Enhanced Quality', 'enhanced_processing', '💎'),
            ('Secure Processing', 'secure_processing', '🔐'),
            ('Advanced Processing', 'advanced_processing', '📄')
        ]
        
        for name, key, icon in processing_types:
            data = file_analysis.get(key, {})
            if data.get('total_records', 0) > 0:
                print(f"   {icon} {name}: {data['total_records']} records ({data['file_count']} files)")
                if data.get('latest_file'):
                    latest = data['latest_file']
                    minutes_ago = (datetime.now() - latest['modified']).total_seconds() / 60
                    print(f"      Latest: {latest['name']} ({minutes_ago:.0f} min ago)")
        
        print(f"\n📈 Total Records Processed: {file_analysis.get('total_records', 0)}")
        
        # Evidence Inventory
        evidence = results.get('evidence_inventory', {})
        if evidence.get('total', 0) > 0:
            print(f"\n📁 EVIDENCE INVENTORY:")
            print(f"   📊 Total Files: {evidence['total']}")
            
            by_type = evidence.get('by_type', {})
            if by_type:
                type_icons = {
                    'images': '🖼️',
                    'documents': '📄',
                    'videos': '🎬',
                    'audio': '🔊',
                    'other': '📁'
                }
                
                for file_type, count in by_type.items():
                    if count > 0:
                        icon = type_icons.get(file_type, '📁')
                        print(f"   {icon} {file_type.title()}: {count}")
        
        # System Performance
        metrics = results.get('system_metrics', {})
        if metrics:
            print(f"\n💻 SYSTEM PERFORMANCE:")
            print(f"   🖥️ CPU Usage: {metrics.get('cpu_usage', 0):.1f}%")
            print(f"   🧠 Memory Usage: {metrics.get('memory_usage', 0):.1f}% ({metrics.get('memory_available_gb', 0):.1f} GB free)")
            print(f"   💾 Disk Usage: {metrics.get('disk_usage', 0):.1f}% ({metrics.get('disk_free_gb', 0):.1f} GB free)")
            print(f"   ⚙️ Active Processes: {metrics.get('active_processes', 0)}")
        
        # Recent Alerts
        if hasattr(self, 'stats') and self.stats.get('alerts'):
            recent_alerts = self.stats['alerts'][-3:]  # Last 3 alerts
            print(f"\n🚨 RECENT ALERTS:")
            for alert in recent_alerts:
                severity_icon = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(alert['severity'], '⚪')
                minutes_ago = (datetime.now() - alert['timestamp']).total_seconds() / 60
                print(f"   {severity_icon} {alert['type']}: {alert['message']} ({minutes_ago:.0f}m ago)")
        
        # Processing Rate
        processing_rate = health.get('processing_rate', 0)
        if processing_rate > 0:
            print(f"\n⚡ Processing Rate: {processing_rate:.1f} records/hour")
        
        print("\n" + "="*70)
        print("💡 Press Ctrl+C to stop monitoring | Updates every 5 seconds")
        print("="*70)

    def run_continuous_monitoring(self):
        """Run continuous monitoring with real-time dashboard."""
        self.log_message("Starting continuous monitoring mode...")
        
        try:
            cycle_count = 0
            
            while True:
                cycle_count += 1
                
                # Perform comprehensive check
                results = self.check_all_processing()
                
                # Display dashboard
                self.display_comprehensive_dashboard(results)
                
                # Wait for next cycle
                time.sleep(self.monitor_config['refresh_interval'])
                
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
            self.log_message("Continuous monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")
            self.logger.error(f"Continuous monitoring failed: {e}")

    def run_single_check(self):
        """Run a single comprehensive check and display results."""
        print("🔍 Performing single comprehensive system check...")
        
        results = self.check_all_processing()
        self.display_comprehensive_dashboard(results)
        
        print("\n✅ Single check completed!")

    def generate_monitoring_report(self) -> Dict:
        """Generate comprehensive monitoring report."""
        self.log_message("Generating comprehensive monitoring report...")
        
        try:
            # Get current status
            results = self.check_all_processing()
            
            # Get historical data from database
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM progress_snapshots 
                WHERE timestamp >= datetime('now', '-24 hours')
                ORDER BY timestamp DESC
            ''')
            
            historical_snapshots = cursor.fetchall()
            
            # Get recent alerts
            cursor.execute('''
                SELECT * FROM alerts 
                WHERE timestamp >= datetime('now', '-24 hours')
                ORDER BY timestamp DESC
            ''')
            
            recent_alerts = cursor.fetchall()
            
            # Compile comprehensive report
            report = {
                'report_timestamp': datetime.now().isoformat(),
                'current_status': results,
                'historical_snapshots_24h': len(historical_snapshots),
                'recent_alerts_24h': len(recent_alerts),
                'trends': self.calculate_trends(historical_snapshots),
                'recommendations': self.generate_recommendations(results),
                'session_summary': {
                    'session_start': self.stats['session_start'].isoformat(),
                    'session_duration_hours': (datetime.now() - self.stats['session_start']).total_seconds() / 3600,
                    'monitoring_cycles': getattr(self, 'monitoring_cycles', 0),
                    'alerts_generated': len(self.stats.get('alerts', []))
                }
            }
            
            # Save report
            report_file = self.reports_folder / f"monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"📊 Monitoring report saved: {report_file}")
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate monitoring report: {e}")
            return {'error': str(e)}

    def calculate_trends(self, snapshots: List) -> Dict:
        """Calculate trends from historical snapshots."""
        if len(snapshots) < 2:
            return {'insufficient_data': True}
        
        try:
            # Extract data points
            cpu_usage = [row[7] for row in snapshots if row[7] is not None]
            memory_usage = [row[6] for row in snapshots if row[6] is not None]
            processing_rate = [row[5] for row in snapshots if row[5] is not None]
            
            trends = {}
            
            # Calculate simple trends (increasing/decreasing)
            if len(cpu_usage) >= 2:
                trends['cpu_trend'] = 'increasing' if cpu_usage[0] > cpu_usage[-1] else 'decreasing'
                trends['avg_cpu'] = sum(cpu_usage) / len(cpu_usage)
            
            if len(memory_usage) >= 2:
                trends['memory_trend'] = 'increasing' if memory_usage[0] > memory_usage[-1] else 'decreasing'
                trends['avg_memory'] = sum(memory_usage) / len(memory_usage)
            
            if len(processing_rate) >= 2:
                trends['processing_trend'] = 'increasing' if processing_rate[0] > processing_rate[-1] else 'decreasing'
                trends['avg_processing_rate'] = sum(processing_rate) / len(processing_rate)
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Failed to calculate trends: {e}")
            return {'error': str(e)}

    def generate_recommendations(self, results: Dict) -> List[str]:
        """Generate intelligent recommendations based on current status."""
        recommendations = []
        
        try:
            # System performance recommendations
            metrics = results.get('system_metrics', {})
            if metrics.get('memory_usage', 0) > 80:
                recommendations.append("High memory usage detected - consider reducing batch sizes")
            
            if metrics.get('cpu_usage', 0) > 90:
                recommendations.append("High CPU usage - consider running fewer concurrent processes")
            
            if metrics.get('disk_usage', 0) > 85:
                recommendations.append("Low disk space - run cleanup or add storage")
            
            # Processing recommendations
            file_analysis = results.get('file_analysis', {})
            if file_analysis.get('total_records', 0) == 0:
                recommendations.append("No processing activity detected - check if processors are running")
            
            # Health-based recommendations
            health = results.get('health_status', {})
            if health.get('last_activity_minutes', 0) > 30:
                recommendations.append("Long period without processing activity - verify system status")
            
            # Evidence recommendations
            evidence = results.get('evidence_inventory', {})
            if evidence.get('total', 0) == 0:
                recommendations.append("No evidence files found - verify evidence directory structure")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {e}")
            return ["Error generating recommendations"]

    def __del__(self):
        """Cleanup database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()


def main():
    """Main monitoring execution with command line options."""
    try:
        monitor = UltimateProgressMonitor()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            mode = sys.argv[1].lower()
            
            if mode == 'continuous' or mode == 'monitor':
                monitor.run_continuous_monitoring()
            elif mode == 'check' or mode == 'single':
                monitor.run_single_check()
            elif mode == 'report':
                report = monitor.generate_monitoring_report()
                if 'error' not in report:
                    print("📊 Monitoring report generated successfully!")
                else:
                    print(f"❌ Report generation failed: {report['error']}")
            else:
                print("❌ Invalid mode. Use: continuous, check, or report")
        else:
            # Default to continuous monitoring
            print("🎮 Starting continuous monitoring mode (default)")
            print("💡 Use 'python ultimate_progress_monitor.py check' for single check")
            print("💡 Use 'python ultimate_progress_monitor.py report' for report generation")
            time.sleep(2)
            monitor.run_continuous_monitoring()
    
    except KeyboardInterrupt:
        print("\n👋 Ultimate Progress Monitor terminated by user")
    except Exception as e:
        print(f"❌ Critical error in monitoring system: {e}")
        logging.error(f"Critical monitoring error: {e}")


if __name__ == "__main__":
    main()