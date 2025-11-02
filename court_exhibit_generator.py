#!/usr/bin/env python3
"""
HARPER'S SAFEWAY HOME - COURT EXHIBIT GENERATOR
Standalone script to generate court-ready PDF from EXHIBIT_INDEX_FDSJ739 CSV

Usage: python court_exhibit_generator.py
"""

import pandas as pd
import os
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

CASE_ID = "FDSJ739"
CSV_FILE = f"legal_exhibits/EXHIBIT_INDEX_{CASE_ID}_20251030_212244.csv"
OUTPUT_DIR = "court_packages"
TOP_N_EXHIBITS = 100  # Adjust to include more/fewer exhibits

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# MAIN LOGIC
# ============================================================================

def load_exhibit_data(csv_path):
    """Load the exhibit index CSV"""
    print(f"Loading exhibit data from: {csv_path}")
    try:
        df = pd.read_csv(csv_path)
        print(f"✓ Loaded {len(df)} total exhibits")
        return df
    except FileNotFoundError:
        print(f"ERROR: File not found: {csv_path}")
        print(f"Expected location: {os.path.abspath(csv_path)}")
        return None

def select_best_exhibits(df, top_n=100):
    """
    Select top exhibits based on:
    1. SHA256 verification status (has hash = higher priority)
    2. Status (SUCCESS > WARNING)
    3. Exhibit numbering order
    """
    print(f"\nFiltering for top {top_n} exhibits...")
    
    # Create scoring system
    df['_has_sha256'] = ~df['SHA256_Hash'].isna() & (df['SHA256_Hash'] != '')
    df['_is_success'] = df['Status'].str.upper() == 'SUCCESS'
    df['_exhibit_num'] = pd.to_numeric(
        df['Exhibit_ID'].str.extract(r'(\d+)')[0], 
        errors='coerce'
    )
    
    # Score exhibits (higher is better)
    df['_score'] = (
        df['_has_sha256'].astype(int) * 100 +  # Has SHA256 = +100 points
        df['_is_success'].astype(int) * 50 +   # Success status = +50 points
        (1 - df['_exhibit_num'].fillna(99999) / 99999) * 10  # Lower numbers = higher score
    )
    
    # Select top N
    top_exhibits = df.nlargest(top_n, '_score').copy()
    top_exhibits = top_exhibits.sort_values('Exhibit_ID')
    
    print(f"✓ Selected {len(top_exhibits)} top exhibits")
    print(f"  - With SHA256 verification: {top_exhibits['_has_sha256'].sum()}")
    print(f"  - With SUCCESS status: {top_exhibits['_is_success'].sum()}")
    
    return top_exhibits

def generate_court_index(exhibits):
    """Generate a court-ready exhibit index"""
    index_data = exhibits[[
        'Exhibit_ID',
        'PDF_Filename',
        'Case_ID',
        'Exhibit_Category',
        'Status',
        'Source_File',
        'SHA256_Hash',
        'Timestamp'
    ]].copy()
    
    index_data = index_data.reset_index(drop=True)
    index_data['Exhibit_Letter'] = [chr(65 + i) if i < 26 else f"{chr(65 + i//26)}{chr(65 + i%26)}" 
                                     for i in range(len(index_data))]
    
    return index_data

def create_court_exhibit_list(exhibits):
    """Create a printable exhibit list for court"""
    
    output = []
    output.append("=" * 100)
    output.append("HARPER'S SAFEWAY HOME - CUSTODY CASE")
    output.append(f"CASE ID: {CASE_ID}")
    output.append(f"EXHIBIT LIST - {datetime.now().strftime('%B %d, %Y')}")
    output.append("=" * 100)
    output.append("")
    
    output.append(f"TOTAL EXHIBITS FOR FILING: {len(exhibits)}")
    output.append("")
    output.append("EXHIBIT MASTER INDEX:")
    output.append("-" * 100)
    output.append(f"{'#':<5} {'Exhibit ID':<30} {'Category':<25} {'Status':<15} {'Source File':<25}")
    output.append("-" * 100)
    
    for idx, (_, row) in enumerate(exhibits.iterrows(), 1):
        exhibit_id = str(row.get('Exhibit_ID', ''))
        category = str(row.get('Exhibit_Category', 'GENERAL'))[:24]
        status = str(row.get('Status', 'UNKNOWN'))[:14]
        source = str(row.get('Source_File', ''))[-24:] if pd.notna(row.get('Source_File')) else ''
        
        output.append(f"{idx:<5} {exhibit_id:<30} {category:<25} {status:<15} {source:<25}")
    
    output.append("-" * 100)
    output.append("")
    output.append("CHAIN OF CUSTODY VERIFICATION:")
    sha256_count = exhibits['SHA256_Hash'].notna().sum()
    output.append(f"  • Total exhibits with SHA256 verification: {sha256_count}/{len(exhibits)}")
    output.append(f"  • Processing date: {exhibits['Timestamp'].iloc[0] if len(exhibits) > 0 else 'N/A'}")
    output.append("")
    output.append("INSTRUCTIONS FOR FILING:")
    output.append("  1. Print all exhibits in sequence")
    output.append("  2. Number pages sequentially")
    output.append("  3. Include this index as cover page")
    output.append("  4. Bind as single document")
    output.append("  5. Submit with signed affidavit")
    output.append("")
    
    return "\n".join(output)

def save_court_index(exhibits):
    """Save the court exhibit index as CSV"""
    index_file = os.path.join(OUTPUT_DIR, f"COURT_EXHIBIT_INDEX_{CASE_ID}_FINAL.csv")
    exhibits.to_csv(index_file, index=False)
    print(f"✓ Saved court exhibit index: {index_file}")
    return index_file

def save_exhibit_list(list_text):
    """Save the printable exhibit list"""
    list_file = os.path.join(OUTPUT_DIR, f"EXHIBIT_LIST_{CASE_ID}_FOR_PRINTING.txt")
    with open(list_file, 'w') as f:
        f.write(list_text)
    print(f"✓ Saved exhibit list: {list_file}")
    return list_file

def main():
    print("\n" + "=" * 80)
    print("HARPER'S SAFEWAY HOME - COURT EXHIBIT GENERATOR")
    print("=" * 80 + "\n")
    
    # Load data
    df = load_exhibit_data(CSV_FILE)
    if df is None:
        return
    
    # Show what we're working with
    print(f"\nDataset columns: {df.columns.tolist()}")
    print(f"Sample row:")
    if len(df) > 0:
        print(df.iloc[0].to_string())
    
    # Select best exhibits
    exhibits = select_best_exhibits(df, TOP_N_EXHIBITS)
    
    # Generate court index
    print("\nGenerating court-ready exhibit index...")
    court_index = generate_court_index(exhibits)
    
    # Create exhibit list
    print("Creating printable exhibit list...")
    exhibit_list = create_court_exhibit_list(court_index)
    
    # Save files
    print("\nSaving files...")
    save_court_index(court_index)
    save_exhibit_list(exhibit_list)
    
    # Print summary
    print("\n" + exhibit_list)
    
    print("\n" + "=" * 80)
    print("✓ COURT EXHIBIT PACKAGE READY FOR MONDAY FILING")
    print("=" * 80)
    print(f"\nOutput files saved to: {os.path.abspath(OUTPUT_DIR)}/")
    print("\nNEXT STEPS:")
    print("  1. Print EXHIBIT_LIST_*_FOR_PRINTING.txt as your cover page")
    print("  2. Gather all exhibits listed in COURT_EXHIBIT_INDEX_*_FINAL.csv")
    print("  3. Organize by exhibit number and bind together")
    print("  4. Submit with court filing Monday")
    print("\n")

if __name__ == "__main__":
    main()
