#!/usr/bin/env python3
"""
Harper's OCR Progress Monitor & Auto-Recovery System
Monitors the OCR processing and automatically restarts if needed
"""

import time
import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path
import psutil
import csv

class OCRMonitor:
    """Monitors and ensures continuous OCR processing"""
    
    def __init__(self):
        self.log_file = Path("logs") / f"ocr_monitor_{datetime.now().strftime('%Y%m%d')}.log"
        self.log_file.parent.mkdir(exist_ok=True)
        self.last_progress_check = 0
        self.process = None
        
    def log_message(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def check_ocr_progress(self):
        """Check if OCR processor is making progress"""
        try:
            # Check if output files are being updated
            output_files = list(Path("output").glob("harper_ocr_results_*.csv"))
            if not output_files:
                return False, "No output files found"
            
            latest_file = max(output_files, key=os.path.getmtime)
            
            # Check file size and modification time
            current_size = latest_file.stat().st_size
            modified_time = latest_file.stat().st_mtime
            
            # If file hasn't been modified in 5 minutes and size hasn't changed
            if time.time() - modified_time > 300:  # 5 minutes
                if current_size == self.last_progress_check:
                    return False, f"No progress detected. File size: {current_size}"
            
            self.last_progress_check = current_size
            
            # Count processed files
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    row_count = sum(1 for row in reader) - 1  # Subtract header
                    return True, f"Processing active. {row_count} files completed."
            except:
                return True, "File being written to"
                
        except Exception as e:
            return False, f"Error checking progress: {e}"
    
    def start_ocr_processor(self):
        """Start the OCR processor"""
        try:
            self.log_message("🚀 Starting OCR processor...")
            
            # Start the process in background
            self.process = subprocess.Popen(
                [sys.executable, "batch_ocr_processor.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=os.getcwd()
            )
            
            self.log_message(f"✅ OCR processor started with PID: {self.process.pid}")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Failed to start OCR processor: {e}")
            return False
    
    def check_process_health(self):
        """Check if the OCR process is still running"""
        if not self.process:
            return False
        
        try:
            # Check if process is still alive
            if self.process.poll() is not None:
                return False
            
            # Check if process is consuming reasonable resources
            try:
                proc = psutil.Process(self.process.pid)
                if proc.status() == psutil.STATUS_ZOMBIE:
                    return False
            except psutil.NoSuchProcess:
                return False
            
            return True
            
        except Exception as e:
            self.log_message(f"⚠️ Error checking process health: {e}")
            return False
    
    def restart_if_needed(self):
        """Restart OCR processor if it's not running or stuck"""
        process_running = self.check_process_health()
        progress_ok, progress_msg = self.check_ocr_progress()
        
        self.log_message(f"📊 Status - Process Running: {process_running}, Progress: {progress_msg}")
        
        if not process_running or not progress_ok:
            self.log_message("🔄 Restarting OCR processor...")
            
            # Kill existing process if it exists
            if self.process:
                try:
                    self.process.terminate()
                    self.process.wait(timeout=10)
                except:
                    try:
                        self.process.kill()
                    except:
                        pass
            
            # Start new process
            return self.start_ocr_processor()
        
        return True
    
    def monitor_loop(self):
        """Main monitoring loop"""
        self.log_message("🎯 Harper's OCR Monitor started")
        self.log_message("📂 Monitoring continuous evidence processing for FDSJ-739-24")
        
        # Start initial process
        self.start_ocr_processor()
        
        try:
            while True:
                time.sleep(60)  # Check every minute
                
                if not self.restart_if_needed():
                    self.log_message("❌ Failed to restart OCR processor, waiting 2 minutes...")
                    time.sleep(120)
                
        except KeyboardInterrupt:
            self.log_message("🛑 Monitor stopped by user")
            if self.process:
                self.process.terminate()
        except Exception as e:
            self.log_message(f"💥 Monitor crashed: {e}")
            # Auto-restart monitor
            time.sleep(30)
            os.execv(sys.executable, [sys.executable] + sys.argv)

def main():
    """Main function"""
    monitor = OCRMonitor()
    monitor.monitor_loop()

if __name__ == "__main__":
    main()