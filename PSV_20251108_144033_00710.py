#!/usr/bin/env python3
"""
Quick Launcher for Harper's Evidence Processor
Simple double-click launcher with dependency checking
"""

import os
import sys
import subprocess
import webbrowser

def check_python():
    """Check if Python is properly installed."""
    try:
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 7):
            print("❌ Python 3.7+ required. Current version:", sys.version)
            return False
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} found")
        return True
    except Exception:
        print("❌ Python check failed")
        return False

def install_dependencies():
    """Install required packages."""
    try:
        print("📦 Installing dependencies...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def check_tesseract():
    """Check if Tesseract is available."""
    try:
        import pytesseract
        # Try to get Tesseract version
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR found: {version}")
        return True
    except Exception:
        print("⚠️  Tesseract OCR not found")
        print("📥 Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        return False

def main():
    """Main launcher function."""
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║              🏛️  HARPER'S EVIDENCE PROCESSOR LAUNCHER  🏛️           ║
    ║                                                                  ║
    ║                      📱 EASY CLICK-TO-RUN 📱                      ║
    ║                                                                  ║
    ║  Case: FDSJ-739-24 | Quick Setup & Launch System                ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    print("🔍 System Check:")
    print("=" * 50)
    
    # Check Python
    if not check_python():
        input("Press Enter to exit...")
        return
    
    # Check if we're in the right directory
    if not os.path.exists('secure_evidence_processor.py'):
        print("❌ Evidence processor not found in current directory")
        print(f"📁 Current directory: {os.getcwd()}")
        input("Press Enter to exit...")
        return
    
    # Install dependencies
    if not install_dependencies():
        input("Press Enter to exit...")
        return
    
    # Check Tesseract (warning only)
    tesseract_ok = check_tesseract()
    
    print("\n" + "=" * 50)
    print("🚀 READY TO LAUNCH!")
    print("=" * 50)
    
    if not tesseract_ok:
        print("⚠️  WARNING: Tesseract OCR not detected")
        print("   OCR functionality may not work properly")
        print("   Install Tesseract from the link above")
        print("")
        choice = input("Continue anyway? (y/n): ").lower()
        if choice != 'y':
            return
    
    print("\n📂 Default password: 'password'")
    print("🔒 Change password in secure_evidence_processor.py if needed")
    print("")
    
    # Launch the processor
    try:
        print("🎯 Launching Harper's Evidence Processor...")
        print("=" * 50)
        
        # Import and run the secure processor
        from secure_evidence_processor import main as processor_main
        processor_main()
        
    except KeyboardInterrupt:
        print("\n\n👋 Launcher interrupted by user")
    except Exception as e:
        print(f"\n❌ Launch failed: {e}")
        print("\nTry running manually:")
        print("python secure_evidence_processor.py")
    
    input("\nPress Enter to close launcher...")

if __name__ == "__main__":
    main()