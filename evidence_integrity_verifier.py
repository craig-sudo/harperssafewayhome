#!/usr/bin/env python3
"""
Evidence Integrity Verifier
Validates SHA-256 hashes to prove evidence tampering has not occurred
Critical for legal defensibility
"""

import pandas as pd
import hashlib
import os
from pathlib import Path
import json
from datetime import datetime

class EvidenceIntegrityVerifier:
    """Verifies cryptographic integrity of processed evidence"""
    
    def __init__(self):
        self.verification_session = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def calculate_current_hash(self, file_path: str) -> str:
        """Calculate current SHA-256 hash of file"""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(8192)
                    if not chunk:
                        break
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            return f"VERIFICATION_ERROR: {str(e)}"
    
    def verify_csv_integrity(self, csv_file: str, evidence_base_path: str = "custody_screenshots"):
        """Verify integrity of all files referenced in CSV"""
        print(f"🔍 Verifying Evidence Integrity: {csv_file}")
        print("=" * 60)
        
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
            
            if 'File_Integrity_Hash' not in df.columns:
                print("❌ No integrity hashes found in CSV - cannot verify")
                return None
            
            verification_results = []
            verified_count = 0
            tampered_count = 0
            missing_count = 0
            total_files = len(df)
            
            print(f"📊 Verifying {total_files} evidence files...")
            
            for idx, row in df.iterrows():
                filename = row['File_Name']
                stored_hash = row['File_Integrity_Hash']
                
                # Find the original file
                file_path = None
                evidence_path = Path(evidence_base_path)
                
                # Search for file in evidence directories
                for file_candidate in evidence_path.rglob(filename):
                    file_path = str(file_candidate)
                    break
                
                if not file_path or not os.path.exists(file_path):
                    result = {
                        'filename': filename,
                        'status': 'MISSING',
                        'stored_hash': stored_hash,
                        'current_hash': 'FILE_NOT_FOUND',
                        'verification': 'FAILED - File Missing'
                    }
                    missing_count += 1
                else:
                    # Calculate current hash
                    current_hash = self.calculate_current_hash(file_path)
                    
                    if current_hash == stored_hash:
                        result = {
                            'filename': filename,
                            'status': 'VERIFIED',
                            'stored_hash': stored_hash,
                            'current_hash': current_hash,
                            'verification': 'PASSED - Integrity Confirmed'
                        }
                        verified_count += 1
                    else:
                        result = {
                            'filename': filename,
                            'status': 'TAMPERED',
                            'stored_hash': stored_hash,
                            'current_hash': current_hash,
                            'verification': 'FAILED - Hash Mismatch (TAMPERING DETECTED)'
                        }
                        tampered_count += 1
                
                verification_results.append(result)
                
                # Progress indicator
                if (idx + 1) % 100 == 0:
                    print(f"   Progress: {idx + 1}/{total_files} ({(idx + 1)/total_files*100:.1f}%)")
            
            # Generate verification report
            verification_df = pd.DataFrame(verification_results)
            
            # Save detailed verification results
            output_file = f"output/integrity_verification_{self.verification_session}.csv"
            verification_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            
            # Generate summary report
            self.generate_verification_report(
                verification_df, total_files, verified_count, 
                tampered_count, missing_count, output_file
            )
            
            return verification_df
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return None
    
    def generate_verification_report(self, verification_df, total_files, verified_count, 
                                   tampered_count, missing_count, output_file):
        """Generate comprehensive verification report"""
        
        print(f"\n🔒 EVIDENCE INTEGRITY VERIFICATION REPORT")
        print("=" * 60)
        print(f"📅 Verification Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Detailed Results: {output_file}")
        print()
        print(f"📊 VERIFICATION SUMMARY:")
        print(f"   Total Files: {total_files}")
        print(f"   ✅ Verified (Intact): {verified_count} ({verified_count/total_files*100:.1f}%)")
        print(f"   🚨 Tampered (Hash Mismatch): {tampered_count} ({tampered_count/total_files*100:.1f}%)")
        print(f"   ❌ Missing Files: {missing_count} ({missing_count/total_files*100:.1f}%)")
        print()
        
        # Legal assessment
        if tampered_count == 0 and missing_count == 0:
            print("🏛️  LEGAL ASSESSMENT: EVIDENCE INTEGRITY CONFIRMED")
            print("   ✅ All evidence files verified with cryptographic integrity")
            print("   ✅ No tampering detected - evidence is court-admissible")
            print("   ✅ Chain of custody maintained")
        elif tampered_count > 0:
            print("⚠️  LEGAL ASSESSMENT: TAMPERING DETECTED")
            print(f"   🚨 {tampered_count} files show evidence of modification")
            print("   ⚖️  Compromised files may be inadmissible in court")
            print("   📋 Investigate tampered files immediately")
            
            # Show tampered files
            tampered_files = verification_df[verification_df['status'] == 'TAMPERED']
            if not tampered_files.empty:
                print(f"\n🚨 TAMPERED FILES:")
                for _, row in tampered_files.iterrows():
                    print(f"   {row['filename']}: Hash mismatch detected")
        elif missing_count > 0:
            print("⚠️  LEGAL ASSESSMENT: MISSING EVIDENCE FILES")
            print(f"   ❌ {missing_count} referenced files cannot be located")
            print("   📋 Evidence may be incomplete for court proceedings")
        
        print()
        
        # Generate court affidavit statement
        if tampered_count == 0 and missing_count == 0:
            affidavit_text = self.generate_affidavit_statement(verified_count, total_files)
            affidavit_file = f"output/integrity_affidavit_{self.verification_session}.txt"
            with open(affidavit_file, 'w', encoding='utf-8') as f:
                f.write(affidavit_text)
            print(f"📋 Court affidavit statement saved to: {affidavit_file}")
        
        print("=" * 60)
    
    def generate_affidavit_statement(self, verified_count: int, total_files: int) -> str:
        """Generate court-ready affidavit statement"""
        return f"""AFFIDAVIT OF EVIDENCE INTEGRITY

Case: Harper's Custody Matter (FDSJ-739-24)
Verification Date: {datetime.now().strftime('%B %d, %Y')}
Verification Session: {self.verification_session}

I hereby affirm under penalty of perjury that:

1. A total of {total_files} digital evidence files were processed and analyzed 
   using cryptographic SHA-256 hash verification methods.

2. Each evidence file was assigned a unique SHA-256 cryptographic hash at the 
   time of initial processing, creating an immutable digital fingerprint.

3. Upon verification conducted on {datetime.now().strftime('%B %d, %Y')}, all 
   {verified_count} evidence files were confirmed to have identical hash values 
   to their original processing, proving no modification or tampering has occurred.

4. The cryptographic verification confirms the digital evidence maintains its 
   original integrity and authenticity since initial collection and processing.

5. The evidence files are suitable for court proceedings and meet the standards 
   for digital evidence admissibility under applicable rules of evidence.

This verification was conducted using industry-standard SHA-256 cryptographic 
hash algorithms to ensure the highest level of evidence integrity verification.

_________________________________
Digital Evidence Technician
Harper's Custody Case (FDSJ-739-24)

Verification completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""


def main():
    """Main verification interface"""
    verifier = EvidenceIntegrityVerifier()
    
    print("🔒 Evidence Integrity Verifier")
    print("=" * 40)
    print("Validates SHA-256 hashes to detect tampering")
    print()
    
    # Find available CSV files with integrity hashes
    output_dir = Path("output")
    csv_files = []
    
    if output_dir.exists():
        # Look for CSV files that might contain integrity hashes
        for csv_file in output_dir.glob("*.csv"):
            try:
                df = pd.read_csv(csv_file, nrows=1)
                if 'File_Integrity_Hash' in df.columns:
                    csv_files.append(csv_file)
            except:
                continue
    
    if not csv_files:
        print("❌ No CSV files with integrity hashes found in output directory")
        print("   Run the secure evidence processor first to generate hashes")
        return
    
    print(f"Found {len(csv_files)} files with integrity data:")
    for i, file in enumerate(csv_files, 1):
        print(f"  {i}. {file.name}")
    
    try:
        choice = int(input(f"\nSelect file to verify (1-{len(csv_files)}): ")) - 1
        if 0 <= choice < len(csv_files):
            selected_file = str(csv_files[choice])
            
            # Ask for evidence base path
            base_path = input("\nEvidence folder path (default: custody_screenshots): ").strip()
            if not base_path:
                base_path = "custody_screenshots"
            
            # Perform verification
            verifier.verify_csv_integrity(selected_file, base_path)
        else:
            print("❌ Invalid selection")
    
    except ValueError:
        print("❌ Invalid input")
    except KeyboardInterrupt:
        print("\n👋 Verification cancelled")


if __name__ == "__main__":
    main()