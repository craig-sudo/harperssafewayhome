#!/usr/bin/env python3
"""
Harper's Performance Monitoring Dashboard - Real-Time System Analytics
Advanced monitoring system with live performance tracking and optimization
Case: FDSJ-739-24 - Performance Intelligence System
"""

import os
import time
import psutil
import threading
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging
from collections import deque, defaultdict
import statistics

class PerformanceMonitor:
    """Real-time performance monitoring and analytics system."""
    
    def __init__(self):
        """Initialize the performance monitoring system."""
        self.monitoring_dir = Path("performance_monitoring")
        self.alerts_dir = Path("performance_alerts")
        self.reports_dir = Path("performance_reports")
        
        # Ensure directories exist
        for directory in [self.monitoring_dir, self.alerts_dir, self.reports_dir]:
            directory.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Initialize performance database
        self.init_performance_database()
        
        # Monitoring configuration
        self.monitoring_interval = 5  # seconds
        self.history_retention = 3600  # 1 hour in seconds
        self.alert_thresholds = {
            'cpu_percent': 85,
            'memory_percent': 90,
            'disk_usage_percent': 95,
            'processing_errors_per_minute': 5,
            'response_time_threshold': 10.0
        }
        
        # Performance data storage
        self.performance_history = {
            'cpu_usage': deque(maxlen=720),  # 1 hour at 5-second intervals
            'memory_usage': deque(maxlen=720),
            'disk_usage': deque(maxlen=720),
            'network_io': deque(maxlen=720),
            'processing_speed': deque(maxlen=720),
            'error_rates': deque(maxlen=720),
            'timestamps': deque(maxlen=720)
        }
        
        # Active monitoring
        self.monitoring_active = False
        self.monitoring_thread = None
        self.alert_handlers = []
        
        # Performance baselines
        self.performance_baselines = {}
        self.load_performance_baselines()
        
        print(f"""
+==================================================================+
|      📊 HARPER'S PERFORMANCE MONITORING DASHBOARD 📊           |
|                                                                  |
|  📈 Real-Time System Performance Analytics                      |
|  🚨 Intelligent Alert System & Optimization                    |
|  ⚡ Advanced Metrics & Performance Intelligence                 |
|                                                                  |
|  📋 Case: FDSJ-739-24                                          |
|  🎯 PERFORMANCE OPTIMIZATION CENTER                             |
+==================================================================+
        """)

    def setup_logging(self):
        """Setup performance monitoring logging."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"performance_monitor_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def init_performance_database(self):
        """Initialize performance monitoring database."""
        db_path = self.monitoring_dir / 'performance_metrics.db'
        
        try:
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.db_lock = threading.Lock()
            
            cursor = self.conn.cursor()
            
            # Create performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_category TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL,
                    metric_unit TEXT,
                    system_load JSON,
                    processing_context TEXT
                )
            ''')
            
            # Create performance alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    alert_level TEXT NOT NULL,
                    alert_category TEXT NOT NULL,
                    alert_message TEXT NOT NULL,
                    metric_value REAL,
                    threshold_value REAL,
                    resolution_status TEXT DEFAULT 'pending',
                    resolution_time TEXT,
                    action_taken TEXT
                )
            ''')
            
            # Create performance baselines table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_baselines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT UNIQUE NOT NULL,
                    baseline_value REAL,
                    variance_tolerance REAL,
                    measurement_count INTEGER DEFAULT 0,
                    last_updated TEXT,
                    calculation_method TEXT
                )
            ''')
            
            # Create system optimization recommendations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS optimization_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    recommendation_category TEXT NOT NULL,
                    recommendation_text TEXT NOT NULL,
                    priority_level INTEGER DEFAULT 5,
                    estimated_impact TEXT,
                    implementation_status TEXT DEFAULT 'pending'
                )
            ''')
            
            self.conn.commit()
            self.logger.info("Performance monitoring database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize performance database: {e}")

    def get_comprehensive_system_metrics(self) -> Dict:
        """Get comprehensive system performance metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('.')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network_io = psutil.net_io_counters()
            
            # Process metrics
            process_count = len(psutil.pids())
            
            # Evidence processing specific metrics
            evidence_dirs = [
                Path("custody_screenshots"),
                Path("custody_screenshots_organized"),
                Path("output"),
                Path("processing_queue") if Path("processing_queue").exists() else None
            ]
            
            total_evidence_files = 0
            total_evidence_size = 0
            
            for dir_path in evidence_dirs:
                if dir_path and dir_path.exists():
                    files = list(dir_path.rglob("*"))
                    files = [f for f in files if f.is_file()]
                    total_evidence_files += len(files)
                    total_evidence_size += sum(f.stat().st_size for f in files)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'load_average_1m': load_avg[0],
                    'load_average_5m': load_avg[1],
                    'load_average_15m': load_avg[2]
                },
                'memory': {
                    'percent': memory.percent,
                    'available_gb': memory.available / (1024**3),
                    'used_gb': memory.used / (1024**3),
                    'total_gb': memory.total / (1024**3),
                    'swap_percent': swap.percent,
                    'swap_used_gb': swap.used / (1024**3)
                },
                'disk': {
                    'percent': disk.percent,
                    'free_gb': disk.free / (1024**3),
                    'used_gb': disk.used / (1024**3),
                    'total_gb': disk.total / (1024**3),
                    'read_count': disk_io.read_count if disk_io else 0,
                    'write_count': disk_io.write_count if disk_io else 0,
                    'read_bytes': disk_io.read_bytes if disk_io else 0,
                    'write_bytes': disk_io.write_bytes if disk_io else 0
                },
                'network': {
                    'bytes_sent': network_io.bytes_sent,
                    'bytes_received': network_io.bytes_recv,
                    'packets_sent': network_io.packets_sent,
                    'packets_received': network_io.packets_recv
                },
                'system': {
                    'process_count': process_count,
                    'uptime_hours': (time.time() - psutil.boot_time()) / 3600
                },
                'evidence_processing': {
                    'total_files': total_evidence_files,
                    'total_size_gb': total_evidence_size / (1024**3),
                    'average_file_size_mb': (total_evidence_size / total_evidence_files / (1024**2)) if total_evidence_files > 0 else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            return {}

    def store_performance_metrics(self, metrics: Dict):
        """Store performance metrics in the database."""
        try:
            timestamp = metrics.get('timestamp', datetime.now().isoformat())
            
            with self.db_lock:
                cursor = self.conn.cursor()
                
                # Store CPU metrics
                cursor.execute('''
                    INSERT INTO performance_metrics 
                    (timestamp, metric_category, metric_name, metric_value, metric_unit, system_load)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (timestamp, 'cpu', 'cpu_percent', metrics['cpu']['percent'], 'percent', 
                      json.dumps(metrics['cpu'])))
                
                # Store memory metrics
                cursor.execute('''
                    INSERT INTO performance_metrics 
                    (timestamp, metric_category, metric_name, metric_value, metric_unit, system_load)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (timestamp, 'memory', 'memory_percent', metrics['memory']['percent'], 'percent',
                      json.dumps(metrics['memory'])))
                
                # Store disk metrics
                cursor.execute('''
                    INSERT INTO performance_metrics 
                    (timestamp, metric_category, metric_name, metric_value, metric_unit, system_load)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (timestamp, 'disk', 'disk_percent', metrics['disk']['percent'], 'percent',
                      json.dumps(metrics['disk'])))
                
                # Store evidence processing metrics
                cursor.execute('''
                    INSERT INTO performance_metrics 
                    (timestamp, metric_category, metric_name, metric_value, metric_unit, system_load)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (timestamp, 'evidence', 'total_files', metrics['evidence_processing']['total_files'], 'count',
                      json.dumps(metrics['evidence_processing'])))
                
                self.conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to store performance metrics: {e}")

    def update_performance_history(self, metrics: Dict):
        """Update in-memory performance history."""
        try:
            current_time = datetime.now()
            
            self.performance_history['timestamps'].append(current_time)
            self.performance_history['cpu_usage'].append(metrics['cpu']['percent'])
            self.performance_history['memory_usage'].append(metrics['memory']['percent'])
            self.performance_history['disk_usage'].append(metrics['disk']['percent'])
            
            # Calculate processing speed (files per minute)
            if len(self.performance_history['timestamps']) >= 2:
                time_diff = (current_time - self.performance_history['timestamps'][-2]).total_seconds() / 60
                file_diff = metrics['evidence_processing']['total_files']
                
                if hasattr(self, 'last_file_count'):
                    file_diff -= self.last_file_count
                
                processing_speed = file_diff / time_diff if time_diff > 0 else 0
                self.performance_history['processing_speed'].append(processing_speed)
            else:
                self.performance_history['processing_speed'].append(0)
            
            self.last_file_count = metrics['evidence_processing']['total_files']
            
            # Network I/O rate
            network_rate = (metrics['network']['bytes_sent'] + metrics['network']['bytes_received']) / (1024**2)  # MB
            self.performance_history['network_io'].append(network_rate)
            
            # Error rate (placeholder - would integrate with error tracking)
            self.performance_history['error_rates'].append(0)
            
        except Exception as e:
            self.logger.error(f"Failed to update performance history: {e}")

    def check_performance_alerts(self, metrics: Dict):
        """Check for performance alerts and trigger notifications."""
        try:
            alerts = []
            
            # CPU usage alert
            if metrics['cpu']['percent'] > self.alert_thresholds['cpu_percent']:
                alerts.append({
                    'level': 'warning' if metrics['cpu']['percent'] < 95 else 'critical',
                    'category': 'cpu',
                    'message': f"High CPU usage: {metrics['cpu']['percent']:.1f}%",
                    'value': metrics['cpu']['percent'],
                    'threshold': self.alert_thresholds['cpu_percent']
                })
            
            # Memory usage alert
            if metrics['memory']['percent'] > self.alert_thresholds['memory_percent']:
                alerts.append({
                    'level': 'critical',
                    'category': 'memory',
                    'message': f"High memory usage: {metrics['memory']['percent']:.1f}%",
                    'value': metrics['memory']['percent'],
                    'threshold': self.alert_thresholds['memory_percent']
                })
            
            # Disk usage alert
            if metrics['disk']['percent'] > self.alert_thresholds['disk_usage_percent']:
                alerts.append({
                    'level': 'critical',
                    'category': 'disk',
                    'message': f"High disk usage: {metrics['disk']['percent']:.1f}%",
                    'value': metrics['disk']['percent'],
                    'threshold': self.alert_thresholds['disk_usage_percent']
                })
            
            # Low available memory alert
            if metrics['memory']['available_gb'] < 1.0:
                alerts.append({
                    'level': 'warning',
                    'category': 'memory',
                    'message': f"Low available memory: {metrics['memory']['available_gb']:.1f} GB",
                    'value': metrics['memory']['available_gb'],
                    'threshold': 1.0
                })
            
            # Process alerts
            for alert in alerts:
                self.process_performance_alert(alert)
            
        except Exception as e:
            self.logger.error(f"Failed to check performance alerts: {e}")

    def process_performance_alert(self, alert: Dict):
        """Process and store a performance alert."""
        try:
            timestamp = datetime.now().isoformat()
            
            # Store alert in database
            with self.db_lock:
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT INTO performance_alerts 
                    (timestamp, alert_level, alert_category, alert_message, 
                     metric_value, threshold_value)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (timestamp, alert['level'], alert['category'], alert['message'],
                      alert['value'], alert['threshold']))
                self.conn.commit()
            
            # Log alert
            if alert['level'] == 'critical':
                self.logger.error(f"CRITICAL ALERT: {alert['message']}")
            else:
                self.logger.warning(f"WARNING ALERT: {alert['message']}")
            
            # Trigger optimization recommendations
            self.generate_optimization_recommendation(alert)
            
        except Exception as e:
            self.logger.error(f"Failed to process performance alert: {e}")

    def generate_optimization_recommendation(self, alert: Dict):
        """Generate optimization recommendations based on alerts."""
        try:
            recommendations = {
                'cpu': [
                    "Consider reducing the number of concurrent processing threads",
                    "Implement processing batching to reduce CPU spikes",
                    "Add delays between intensive operations"
                ],
                'memory': [
                    "Reduce batch size for evidence processing",
                    "Implement memory cleanup between processing batches",
                    "Consider processing files in smaller chunks"
                ],
                'disk': [
                    "Archive old processing results to external storage",
                    "Clean up temporary processing files",
                    "Implement automatic cleanup of old logs and reports"
                ]
            }
            
            category = alert['category']
            if category in recommendations:
                for recommendation in recommendations[category]:
                    with self.db_lock:
                        cursor = self.conn.cursor()
                        cursor.execute('''
                            INSERT INTO optimization_recommendations 
                            (timestamp, recommendation_category, recommendation_text, 
                             priority_level, estimated_impact)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (datetime.now().isoformat(), category, recommendation,
                              3 if alert['level'] == 'critical' else 5, 'medium'))
                        self.conn.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to generate optimization recommendation: {e}")

    def calculate_performance_statistics(self) -> Dict:
        """Calculate performance statistics from historical data."""
        try:
            stats = {}
            
            for metric_name, data in self.performance_history.items():
                if metric_name == 'timestamps' or len(data) == 0:
                    continue
                
                stats[metric_name] = {
                    'current': data[-1] if data else 0,
                    'average': statistics.mean(data) if data else 0,
                    'min': min(data) if data else 0,
                    'max': max(data) if data else 0,
                    'median': statistics.median(data) if data else 0,
                    'std_dev': statistics.stdev(data) if len(data) > 1 else 0
                }
            
            # Calculate trend indicators
            if len(self.performance_history['cpu_usage']) >= 10:
                recent_cpu = list(self.performance_history['cpu_usage'])[-10:]
                older_cpu = list(self.performance_history['cpu_usage'])[-20:-10] if len(self.performance_history['cpu_usage']) >= 20 else []
                
                if older_cpu:
                    cpu_trend = statistics.mean(recent_cpu) - statistics.mean(older_cpu)
                    stats['trends'] = {'cpu_trend': cpu_trend}
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to calculate performance statistics: {e}")
            return {}

    def start_monitoring(self):
        """Start continuous performance monitoring."""
        if self.monitoring_active:
            self.logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("Performance monitoring started")

    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        
        self.logger.info("Performance monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Get current metrics
                metrics = self.get_comprehensive_system_metrics()
                
                if metrics:
                    # Store metrics
                    self.store_performance_metrics(metrics)
                    
                    # Update history
                    self.update_performance_history(metrics)
                    
                    # Check for alerts
                    self.check_performance_alerts(metrics)
                
                # Wait for next monitoring interval
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)

    def generate_performance_report(self, hours_back: int = 24) -> str:
        """Generate comprehensive performance report."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.reports_dir / f"performance_report_{timestamp}.html"
            
            # Calculate report period
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours_back)
            
            # Get performance statistics
            stats = self.calculate_performance_statistics()
            
            # Get recent alerts
            with self.db_lock:
                cursor = self.conn.cursor()
                cursor.execute('''
                    SELECT alert_level, alert_category, alert_message, timestamp
                    FROM performance_alerts 
                    WHERE timestamp >= ? 
                    ORDER BY timestamp DESC 
                    LIMIT 20
                ''', (start_time.isoformat(),))
                recent_alerts = cursor.fetchall()
            
            # Generate HTML report
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Performance Monitoring Report - Harper's Evidence Processing</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; }}
        .summary {{ background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 5px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }}
        .metric-box {{ background: white; padding: 15px; border-left: 4px solid #007acc; }}
        .alert-critical {{ color: #dc3545; }}
        .alert-warning {{ color: #ffc107; }}
        .footer {{ margin-top: 40px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 PERFORMANCE MONITORING REPORT</h1>
        <h2>Harper's Evidence Processing System</h2>
        <p><strong>Report Period:</strong> {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}</p>
    </div>
    
    <div class="summary">
        <h3>SYSTEM PERFORMANCE SUMMARY</h3>
        <div class="metrics">
            """
            
            # Add performance metrics
            for metric_name, metric_stats in stats.items():
                if isinstance(metric_stats, dict):
                    html_content += f"""
            <div class="metric-box">
                <h4>{metric_name.replace('_', ' ').title()}</h4>
                <p><strong>Current:</strong> {metric_stats.get('current', 0):.2f}</p>
                <p><strong>Average:</strong> {metric_stats.get('average', 0):.2f}</p>
                <p><strong>Peak:</strong> {metric_stats.get('max', 0):.2f}</p>
            </div>
                    """
            
            html_content += f"""
        </div>
    </div>
    
    <h3>RECENT ALERTS ({len(recent_alerts)} total)</h3>
    <div style="max-height: 300px; overflow-y: auto;">
        """
            
            for alert in recent_alerts:
                level_class = f"alert-{alert[0]}"
                html_content += f"""
        <div class="{level_class}" style="padding: 8px; margin: 4px 0; border-left: 3px solid;">
            <strong>{alert[0].upper()}:</strong> {alert[2]} 
            <span style="float: right; font-size: 12px;">{alert[3]}</span>
        </div>
                """
            
            html_content += f"""
    </div>
    
    <div class="footer">
        <p><strong>Generated by:</strong> Harper's Performance Monitoring System v2.0</p>
        <p><strong>Report ID:</strong> PERF_{timestamp}</p>
    </div>
</body>
</html>
            """
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Performance report generated: {report_file}")
            return str(report_file)
            
        except Exception as e:
            self.logger.error(f"Failed to generate performance report: {e}")
            return None

    def load_performance_baselines(self):
        """Load performance baselines from database."""
        try:
            with self.db_lock:
                cursor = self.conn.cursor()
                cursor.execute('SELECT metric_name, baseline_value FROM performance_baselines')
                baselines = cursor.fetchall()
                
                for metric_name, baseline_value in baselines:
                    self.performance_baselines[metric_name] = baseline_value
            
        except Exception as e:
            self.logger.error(f"Failed to load performance baselines: {e}")

    def interactive_menu(self):
        """Interactive menu for performance monitoring."""
        while True:
            print("\n" + "="*60)
            print("📊 PERFORMANCE MONITORING DASHBOARD")
            print("="*60)
            print("[1] 🚀 Start Performance Monitoring")
            print("[2] 🛑 Stop Performance Monitoring")
            print("[3] 📈 View Live Performance Stats")
            print("[4] 🚨 View Recent Alerts")
            print("[5] 📋 Generate Performance Report")
            print("[6] ⚙️ Configure Alert Thresholds")
            print("[7] 🔧 System Optimization Recommendations")
            print("[0] 🚪 Exit")
            print("="*60)
            
            if self.monitoring_active:
                print("🟢 Monitoring Status: ACTIVE")
            else:
                print("🔴 Monitoring Status: INACTIVE")
            
            try:
                choice = input("🎯 Select option: ").strip()
                
                if choice == '1':
                    self.start_monitoring()
                    print("✅ Performance monitoring started")
                
                elif choice == '2':
                    self.stop_monitoring()
                    print("✅ Performance monitoring stopped")
                
                elif choice == '3':
                    self.show_live_performance_stats()
                
                elif choice == '4':
                    self.show_recent_alerts()
                
                elif choice == '5':
                    hours = int(input("📅 Hours of data to include (default 24): ").strip() or "24")
                    report_path = self.generate_performance_report(hours)
                    if report_path:
                        print(f"📋 Report generated: {report_path}")
                
                elif choice == '6':
                    self.configure_alert_thresholds()
                
                elif choice == '7':
                    self.show_optimization_recommendations()
                
                elif choice == '0':
                    print("👋 Exiting Performance Monitoring Dashboard")
                    self.stop_monitoring()
                    break
                
                else:
                    print("❌ Invalid option. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting Performance Monitoring Dashboard")
                self.stop_monitoring()
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def show_live_performance_stats(self):
        """Display live performance statistics."""
        print("\n📈 LIVE PERFORMANCE STATISTICS")
        print("="*50)
        
        metrics = self.get_comprehensive_system_metrics()
        if metrics:
            print(f"🖥️ CPU Usage: {metrics['cpu']['percent']:.1f}%")
            print(f"🧠 Memory Usage: {metrics['memory']['percent']:.1f}%")
            print(f"💾 Disk Usage: {metrics['disk']['percent']:.1f}%")
            print(f"📁 Evidence Files: {metrics['evidence_processing']['total_files']:,}")
            print(f"💽 Evidence Size: {metrics['evidence_processing']['total_size_gb']:.1f} GB")
            print(f"⚡ Available Memory: {metrics['memory']['available_gb']:.1f} GB")
        else:
            print("❌ Unable to retrieve performance metrics")
        
        print("="*50)

    def show_recent_alerts(self):
        """Display recent performance alerts."""
        print("\n🚨 RECENT PERFORMANCE ALERTS")
        print("="*50)
        
        try:
            with self.db_lock:
                cursor = self.conn.cursor()
                cursor.execute('''
                    SELECT alert_level, alert_message, timestamp
                    FROM performance_alerts 
                    ORDER BY timestamp DESC 
                    LIMIT 10
                ''')
                alerts = cursor.fetchall()
                
                if alerts:
                    for alert in alerts:
                        level_icon = "🚨" if alert[0] == 'critical' else "⚠️"
                        print(f"{level_icon} {alert[1]} ({alert[2]})")
                else:
                    print("✅ No recent alerts")
        except Exception as e:
            print(f"❌ Error retrieving alerts: {e}")
        
        print("="*50)

    def configure_alert_thresholds(self):
        """Interactive alert threshold configuration."""
        print("\n⚙️ CONFIGURE ALERT THRESHOLDS")
        print("="*50)
        
        for threshold_name, current_value in self.alert_thresholds.items():
            print(f"{threshold_name}: {current_value}")
        
        threshold_name = input("📋 Threshold to modify (or press Enter to skip): ").strip()
        if threshold_name in self.alert_thresholds:
            new_value = float(input(f"💭 New value for {threshold_name} (current: {self.alert_thresholds[threshold_name]}): ").strip())
            self.alert_thresholds[threshold_name] = new_value
            print(f"✅ Updated {threshold_name} to {new_value}")

    def show_optimization_recommendations(self):
        """Show system optimization recommendations."""
        print("\n🔧 OPTIMIZATION RECOMMENDATIONS")
        print("="*50)
        
        try:
            with self.db_lock:
                cursor = self.conn.cursor()
                cursor.execute('''
                    SELECT recommendation_text, priority_level, estimated_impact
                    FROM optimization_recommendations 
                    WHERE implementation_status = 'pending'
                    ORDER BY priority_level ASC
                    LIMIT 10
                ''')
                recommendations = cursor.fetchall()
                
                if recommendations:
                    for i, rec in enumerate(recommendations, 1):
                        priority = "🔴" if rec[1] <= 3 else "🟡" if rec[1] <= 6 else "🟢"
                        print(f"{priority} {i}. {rec[0]} (Impact: {rec[2]})")
                else:
                    print("✅ No pending optimization recommendations")
        except Exception as e:
            print(f"❌ Error retrieving recommendations: {e}")
        
        print("="*50)

    def __del__(self):
        """Cleanup resources."""
        self.stop_monitoring()
        if hasattr(self, 'conn'):
            self.conn.close()


def main():
    """Main execution function."""
    try:
        performance_monitor = PerformanceMonitor()
        
        # Check command line arguments
        import sys
        if len(sys.argv) > 1:
            if sys.argv[1] in ['--help', '-h', 'help']:
                print("Harper's Performance Monitoring Dashboard")
                print("Usage: python performance_monitor.py [options]")
                print("Options:")
                print("  start    - Start monitoring automatically")
                print("  report   - Generate performance report")
                print("  (no args) - Interactive mode")
                return
            elif sys.argv[1] == 'start':
                performance_monitor.start_monitoring()
                print("Performance monitoring started. Press Ctrl+C to stop.")
                try:
                    while True:
                        time.sleep(60)
                        stats = performance_monitor.calculate_performance_statistics()
                        print(f"📊 CPU: {stats.get('cpu_usage', {}).get('current', 0):.1f}% | "
                              f"Memory: {stats.get('memory_usage', {}).get('current', 0):.1f}% | "
                              f"Disk: {stats.get('disk_usage', {}).get('current', 0):.1f}%")
                except KeyboardInterrupt:
                    print("\nStopping monitoring...")
                finally:
                    performance_monitor.stop_monitoring()
            elif sys.argv[1] == 'report':
                report_path = performance_monitor.generate_performance_report()
                if report_path:
                    print(f"📋 Report generated: {report_path}")
        else:
            # Interactive mode
            performance_monitor.interactive_menu()
    
    except KeyboardInterrupt:
        print("\n👋 Performance Monitoring Dashboard terminated by user")
    except Exception as e:
        print(f"❌ Critical error in Performance Monitoring Dashboard: {e}")
        logging.error(f"Critical error: {e}")


if __name__ == "__main__":
    main()