#!/usr/bin/env python3
"""
Harper's Evidence Processing - Quick Test Harness
Runs basic verification tests for all evidence processing tools
Case: FDSJ-739-24 - System Verification
"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

def run_command(command, description, timeout=60):
    """Run a command and return the result."""
    print(f"🔍 {description}")
    print(f"💻 Command: {command}")
    
    try:
        start_time = time.time()
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ SUCCESS ({duration:.1f}s)")
            if result.stdout.strip():
                print(f"📄 Output:\n{result.stdout.strip()[:500]}")
                if len(result.stdout.strip()) > 500:
                    print("   ... (output truncated)")
        else:
            print(f"❌ FAILED ({duration:.1f}s) - Exit code: {result.returncode}")
            if result.stderr.strip():
                print(f"🚨 Error:\n{result.stderr.strip()[:500]}")
        
        print("-" * 60)
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT after {timeout}s")
        print("-" * 60)
        return False
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")
        print("-" * 60)
        return False

def main():
    """Run the quick test harness."""
    print("""
+==================================================================+
|       🧪 HARPER'S EVIDENCE PROCESSING - QUICK TEST HARNESS      |
|                                                                  |
|  🔍 System Verification & Smoke Testing                         |
|  ⚡ Quick validation of all processing tools                    |
|  📋 Case: FDSJ-739-24                                          |
|                                                                  |""" + f"|  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                                    |" + """
+==================================================================+
    """)
    
    # Test results tracking
    tests = []
    
    print("🚀 STARTING SYSTEM VERIFICATION TESTS")
    print("=" * 60)
    
    # Test 1: Python environment check
    tests.append(run_command(
        "python --version",
        "Verify Python installation",
        10
    ))
    
    # Test 2: Syntax validation
    print("🔍 SYNTAX VALIDATION TESTS")
    
    test_files = [
        "evidence_integrity_checker.py",
        "court_package_exporter.py", 
        "duplicate_file_manager.py",
        "master_control_system.py",
        "advanced_evidence_processor.py"
    ]
    
    for file in test_files:
        if Path(file).exists():
            tests.append(run_command(
                f"python -m py_compile {file}",
                f"Syntax check: {file}",
                15
            ))
        else:
            print(f"⚠️ File not found: {file}")
    
    # Test 3: Evidence Integrity Checker
    print("🛡️ EVIDENCE INTEGRITY CHECKER TESTS")
    
    tests.append(run_command(
        "python evidence_integrity_checker.py stats",
        "Evidence Integrity Checker - Stats Mode",
        30
    ))
    
    # Test 4: Court Package Exporter
    print("⚖️ COURT PACKAGE EXPORTER TESTS")
    
    # Test with a dry-run mode (check if tool has help/info mode)
    tests.append(run_command(
        "python court_package_exporter.py --help",
        "Court Package Exporter - Help Mode",
        20
    ))
    
    # Test 5: Duplicate File Manager
    print("🗑️ DUPLICATE FILE MANAGER TESTS")
    
    tests.append(run_command(
        "python duplicate_file_manager.py --help",
        "Duplicate File Manager - Help Mode", 
        20
    ))
    
    # Test 6: Master Control System
    print("🎛️ MASTER CONTROL SYSTEM TESTS")
    
    tests.append(run_command(
        "python master_control_system.py --help",
        "Master Control System - Help Mode",
        20
    ))
    
    # Test 7: Directory structure validation
    print("📁 DIRECTORY STRUCTURE VALIDATION")
    
    required_dirs = [
        "custody_screenshots",
        "output", 
        "logs",
        "config"
    ]
    
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"✅ Directory exists: {directory}")
            tests.append(True)
        else:
            print(f"⚠️ Directory missing: {directory}")
            tests.append(False)
    
    # Test Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(tests)
    total = len(tests)
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"📊 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready for evidence processing.")
        print("💡 You can now run any of the evidence processing tools safely.")
    elif passed >= total * 0.8:
        print("\n⚠️ Most tests passed. Minor issues detected.")
        print("💡 System should work but review failed tests above.")
    else:
        print("\n🚨 Multiple test failures detected!")
        print("💡 Please review errors above before processing evidence.")
    
    # Quick usage guide
    print(f"\n📋 QUICK USAGE GUIDE")
    print("=" * 60)
    print("🚀 Windows Launcher:")
    print("   MASTER_LAUNCHER.bat")
    print("")
    print("🎛️ Python Master Control:")
    print("   python master_control_system.py")
    print("")
    print("🛡️ Integrity Check:")
    print("   python evidence_integrity_checker.py")
    print("")
    print("⚖️ Court Package:")
    print("   python court_package_exporter.py focused")
    print("")
    print("🗑️ Find Duplicates:")
    print("   python duplicate_file_manager.py")
    print("")
    print("📋 Processing Report:")
    print("   python advanced_evidence_processor.py")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Test harness interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test harness failed: {e}")
        sys.exit(1)