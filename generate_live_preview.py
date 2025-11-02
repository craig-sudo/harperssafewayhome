#!/usr/bin/env python3
"""
Generate a live preview while the full OCR batch runs.
Samples a subset of images and writes a human-readable preview and a small CSV.
"""
from pathlib import Path
import random
from datetime import datetime
import csv

from enhanced_ocr_processor import EnhancedOCRProcessor


def pick_sample_images(root: Path, limit: int = 25):
    exts = {'.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'}
    files = [p for p in root.rglob('*') if p.suffix.lower() in exts]
    # Prefer recently modified files
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    # Take top 200 recents then random sample to diversify
    pool = files[:200] if len(files) > 200 else files
    if len(pool) <= limit:
        return pool
    return random.sample(pool, k=limit)


def main():
    input_dir = Path('custody_screenshots')
    out_dir = Path('output')
    out_dir.mkdir(exist_ok=True)
    
    processor = EnhancedOCRProcessor()

    sample = pick_sample_images(input_dir, limit=25)
    if not sample:
        print('No images found to preview.')
        return

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    txt_path = out_dir / 'ENHANCED_PREVIEW_NOW.txt'
    csv_path = out_dir / f'enhanced_preview_sample_{ts}.csv'

    rows = []
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write('=== Enhanced OCR Live Preview ===\n')
        f.write(f'Generated: {datetime.now().isoformat(timespec="seconds")}\n')
        f.write(f'Total samples: {len(sample)}\n')
        f.write('='*80 + '\n\n')
        
        for img in sample:
            res = processor.process_image(img)
            if not res:
                continue
            rows.append(res)
            
            f.write(f'--- File: {res["filename"]} ---\n')
            f.write(f'Path: {res["filepath"]}\n')
            f.write(f'Sender: {res["sender"]}\n')
            f.write(f'Recipient: {res["recipient"]}\n')
            f.write('Formatted Text:\n')
            f.write(res['formatted_text'][:1500] + ('\n...[truncated]\n' if len(res['formatted_text'])>1500 else '\n'))
            f.write('\n' + '='*80 + '\n\n')

    # Write small CSV
    with open(csv_path, 'w', encoding='utf-8', newline='') as cf:
        writer = csv.DictWriter(cf, fieldnames=['filename','filepath','sender','recipient','char_count','formatted_text'])
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, '') for k in writer.fieldnames})

    print(f'Wrote preview: {txt_path.resolve()}')
    print(f'Wrote sample CSV: {csv_path.resolve()}')


if __name__ == '__main__':
    main()
