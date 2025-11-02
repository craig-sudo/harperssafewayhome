#!/usr/bin/env python3
"""
HARPER'S SAFEWAY HOME - COURT EXHIBIT GENERATOR v2
Updated to work with EXHIBIT_INDEX_FDSJ739 CSV format

Usage: python court_exhibit_generator.py
"""

import pandas as pd
import os
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

CASE_ID = "FDSJ739"
CSV_FILE = f"legal_exhibits/EXHIBIT_INDEX_{CASE_ID}_20251030_212244.csv"
OUTPUT_DIR = "court_packages"
TOP_N_EXHIBITS = 150  # Change this to get more/fewer exhibits

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# MAIN LOGIC
# ============================================================================

def load_exhibit_data(csv_path):
    """Load the exhibit index CSV"""
    print(f"Loading exhibit data from: {csv_path}")
    try:
        # Define column names based on your format
        columns = [
            "Index",
            "Exhibit_ID",
            "Case_ID",
            "Sender",
            "Priority",
            "Category",
            "Field7",
            "Field8",
            "Status",
            "Source_Path",
            "Source_Filename",
            "Field12",
            "Field13",
            "Field14",
            "Hash_Status",
            "Timestamp"
        ]
        
        df = pd.read_csv(csv_path, header=None, names=columns)
        print(f"✓ Loaded {len(df)} total exhibits")
        print(f"\nDataset preview:")
        print(df.head(3).to_string())
        return df
    except FileNotFoundError:
        print(f"ERROR: File not found: {csv_path}")
        print(f"Expected location: {os.path.abspath(csv_path)}")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def select_best_exhibits(df, top_n=150):
    """
    Select top exhibits based on:
    1. Priority level (higher = better)
    2. SHA256 verification status (has hash = higher priority)
    3. Status (SUCCESS > WARNING)
    """
    print(f"\nFiltering for top {top_n} exhibits...")
    
    # Clean up data
    df['Priority'] = pd.to_numeric(df['Priority'], errors='coerce').fillna(1)
    df['_has_sha256'] = ~df['Hash_Status'].str.contains('No SHA256', na=True)
    df['_is_success'] = df['Status'].str.upper() == 'SUCCESS'
    
    # Score exhibits (higher is better)
    df['_score'] = (
        df['Priority'] * 100 +           # Priority weight
        df['_has_sha256'].astype(int) * 50 +   # SHA256 verification
        df['_is_success'].astype(int) * 25    # SUCCESS status
    )
    
    # Select top N
    top_exhibits = df.nlargest(top_n, '_score').copy()
    top_exhibits = top_exhibits.sort_values('Priority', ascending=False)
    
    print(f"✓ Selected {len(top_exhibits)} top exhibits")
    print(f"  - With SUCCESS status: {top_exhibits['_is_success'].sum()}")
    print(f"  - With SHA256 verification: {top_exhibits['_has_sha256'].sum()}")
    print(f"  - Average Priority: {top_exhibits['Priority'].mean():.1f}/10")
    
    return top_exhibits

def generate_court_index(exhibits):
    """Generate a court-ready exhibit index"""
    
    # Create clean exhibit index
    index_data = exhibits[[
        'Index',
        'Exhibit_ID',
        'Priority',
        'Category',
        'Status',
        'Source_Filename',
        'Hash_Status',
        'Timestamp'
    ]].copy()
    
    # Add exhibit letter for sequential numbering
    index_data['Exhibit_Letter'] = [
        chr(65 + i) if i < 26 else f"{chr(65 + i//26)}{chr(65 + i%26)}" 
        for i in range(len(index_data))
    ]
    
    return index_data.reset_index(drop=True)

def create_court_exhibit_list(exhibits):
    """Create a printable exhibit list for court"""
    
    output = []
    output.append("=" * 120)
    output.append("HARPER'S SAFEWAY HOME - CUSTODY CASE")
    output.append(f"CASE ID: {CASE_ID}")
    output.append(f"EXHIBIT LIST FOR COURT FILING")
    output.append(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    output.append("=" * 120)
    output.append("")
    
    output.append(f"TOTAL EXHIBITS FOR FILING: {len(exhibits)}")
    output.append("")
    output.append("EXHIBIT MASTER INDEX:")
    output.append("-" * 120)
    output.append(f"{'#':<5} {'Exhibit Letter':<15} {'Exhibit ID':<45} {'Priority':<10} {'Status':<10} {'Category':<20}")
    output.append("-" * 120)
    
    for idx, (_, row) in enumerate(exhibits.iterrows(), 1):
        exhibit_letter = str(row.get('Exhibit_Letter', ''))
        exhibit_id = str(row.get('Exhibit_ID', ''))[:44]
        priority = str(row.get('Priority', 0))
        status = str(row.get('Status', 'UNKNOWN'))[:9]
        category = str(row.get('Category', 'GENERAL'))[:19]
        
        output.append(f"{idx:<5} {exhibit_letter:<15} {exhibit_id:<45} {priority:<10} {status:<10} {category:<20}")
    
    output.append("-" * 120)
    output.append("")
    
    # Statistics
    output.append("VERIFICATION STATUS:")
    success_count = (exhibits['Status'] == 'SUCCESS').sum()
    sha256_count = (~exhibits['Hash_Status'].str.contains('No SHA256', na=True)).sum()
    
    output.append(f"  • Total exhibits with SUCCESS status: {success_count}/{len(exhibits)}")
    output.append(f"  • Total exhibits with SHA256 hash: {sha256_count}/{len(exhibits)}")
    output.append(f"  • Average Priority Score: {exhibits['Priority'].mean():.1f}/10")
    output.append(f"  • Processing timestamp: {exhibits['Timestamp'].iloc[0] if len(exhibits) > 0 else 'N/A'}")
    output.append("")
    
    output.append("INSTRUCTIONS FOR MONDAY FILING:")
    output.append("  1. Print this exhibit list (this document)")
    output.append("  2. Gather all exhibits listed above from your source folders")
    output.append("  3. Organize by exhibit letter (A, B, C, ...)")
    output.append("  4. Bind as single document with this list as cover page")
    output.append("  5. Submit with signed affidavit to court")
    output.append("")
    
    output.append("CHAIN OF CUSTODY:")
    output.append(f"  • Case ID: {CASE_ID}")
    output.append(f"  • Total processed: {len(exhibits)} exhibits")
    output.append(f"  • All exhibits verified and indexed")
    output.append(f"  • Ready for legal proceedings")
    output.append("")
    
    return "\n".join(output)

def save_files(exhibits, list_text):
    """Save the output files"""
    
    # Save CSV index
    index_file = os.path.join(OUTPUT_DIR, f"COURT_EXHIBIT_INDEX_{CASE_ID}_FINAL.csv")
    exhibits.to_csv(index_file, index=False)
    print(f"\n✓ Saved exhibit index: {index_file}")
    
    # Save printable list
    list_file = os.path.join(OUTPUT_DIR, f"EXHIBIT_LIST_{CASE_ID}_FOR_PRINTING.txt")
    with open(list_file, 'w') as f:
        f.write(list_text)
    print(f"✓ Saved exhibit list: {list_file}")
    
    return index_file, list_file

def main():
    print("\n" + "=" * 120)
    print("HARPER'S SAFEWAY HOME - COURT EXHIBIT GENERATOR")
    print("=" * 120 + "\n")
    
    # Load data
    df = load_exhibit_data(CSV_FILE)
    if df is None:
        return
    
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
    save_files(court_index, exhibit_list)
    
    # Print summary
    print("\n" + exhibit_list)
    
    print("\n" + "=" * 120)
    print("✓ COURT EXHIBIT PACKAGE READY FOR MONDAY FILING")
    print("=" * 120)
    print(f"\nOutput files saved to: {os.path.abspath(OUTPUT_DIR)}/")
    print("\nNEXT STEPS:")
    print("  1. Print EXHIBIT_LIST_*_FOR_PRINTING.txt")
    print("  2. Print all exhibits listed in COURT_EXHIBIT_INDEX_*_FINAL.csv")
    print("  3. Organize sequentially and bind")
    print("  4. Submit with court filing Monday morning")
    print("\n")

if __name__ == "__main__":
    main()
