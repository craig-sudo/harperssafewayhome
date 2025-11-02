#!/bin/bash

echo ""
echo "==============================================================="
echo "         HARPER'S EVIDENCE PROCESSOR - QUICK LAUNCHER"
echo "                     FDSJ-739-24 Case System"
echo "==============================================================="
echo ""

# Check Python installation
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python not found!"
        echo "Please install Python from: https://python.org/downloads"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Python found. Checking dependencies..."
echo ""

# Check if we're in the right directory
if [ ! -f "secure_evidence_processor.py" ]; then
    echo "ERROR: Please run this launcher from the Harper's evidence processor folder"
    echo "Current directory: $(pwd)"
    exit 1
fi

# Install dependencies if needed
echo "Installing/updating required packages..."
$PYTHON_CMD -m pip install -r requirements.txt

echo ""
echo "==============================================================="
echo "              LAUNCHING SECURE EVIDENCE PROCESSOR"
echo "==============================================================="
echo ""
echo "Password: password"
echo "(Default password - change in secure_evidence_processor.py)"
echo ""

# Launch the secure processor
$PYTHON_CMD secure_evidence_processor.py

echo ""
echo "==============================================================="
echo "                   SESSION COMPLETE"
echo "==============================================================="