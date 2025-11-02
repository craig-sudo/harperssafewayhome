#!/usr/bin/env python3
"""
Standalone live preview generator without importing enhanced_ocr_processor
(to avoid interfering with the long-running batch).
"""
from pathlib import Path
from datetime import datetime
import random
import re
import csv

import pytesseract
import cv2
from PIL import Image

# Set Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


def preprocess_image(image_path: Path):
    img = cv2.imread(str(image_path))
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray)
    binary = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return Image.fromarray(binary)


def clean_text(text: str) -> str:
    lines = [l.strip() for l in text.split('\n')]
    out = []
    for line in lines:
        if not line or len(line) < 2:
            continue
        if re.match(r"^(iMessage|WhatsApp|Messenger|Messages|Delivered|Read|Sent)$", line, re.I):
            continue
        if re.match(r"^\d{1,2}:\d{2}$", line):
            continue
        out.append(re.sub(r"\s{2,}", " ", line))
    result = "\n".join(out).strip()
    return re.sub(r"\n{3,}", "\n\n", result)


def detect_sender_recipient(text: str, filename: str):
    sender = "Dale"
    recipient = "Unknown"
    lowf = filename.lower()
    lowt = text.lower()
    if 'emma' in lowf or 'emma' in lowt[:150]:
        recipient = 'Emma'
    elif 'jane' in lowf or 'nanny' in lowf:
        recipient = 'Jane (Nanny)'
    elif any(k in lowf for k in ['mom','mother','mama']):
        recipient = 'Mom'
    m = re.search(r"to[:\s]+([^\n]+)", text, re.I)
    if m:
        recipient = m.group(1).strip()[:60]
    return sender, recipient


def pick_sample_images(root: Path, limit: int = 25):
    exts = {'.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'}
    files = [p for p in root.rglob('*') if p.suffix.lower() in exts]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    pool = files[:200] if len(files) > 200 else files
    if len(pool) <= limit:
        return pool
    return random.sample(pool, k=limit)


def main():
    input_dir = Path('custody_screenshots')
    out_dir = Path('output'); out_dir.mkdir(exist_ok=True)
    sample = pick_sample_images(input_dir, 25)
    if not sample:
        print('No images found')
        return
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    txt_path = out_dir / 'ENHANCED_PREVIEW_NOW.txt'
    csv_path = out_dir / f'enhanced_preview_sample_{ts}.csv'
    rows = []
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write('=== Enhanced OCR Live Preview (Standalone) ===\n')
        f.write(f'Generated: {datetime.now().isoformat(timespec="seconds")}\n')
        f.write(f'Total samples: {len(sample)}\n')
        f.write('='*80 + '\n\n')
        for img in sample:
            pil = preprocess_image(img)
            if pil is None:
                continue
            text = pytesseract.image_to_string(pil)
            formatted = clean_text(text)
            sender, recipient = detect_sender_recipient(formatted, img.name)
            rows.append({
                'filename': img.name,
                'filepath': str(img),
                'sender': sender,
                'recipient': recipient,
                'formatted_text': formatted,
                'char_count': len(formatted)
            })
            f.write(f'--- File: {img.name} ---\n')
            f.write(f'Path: {img}\n')
            f.write(f'Sender: {sender}\n')
            f.write(f'Recipient: {recipient}\n')
            f.write('Formatted Text:\n')
            f.write(formatted[:1500] + ('\n...[truncated]\n' if len(formatted)>1500 else '\n'))
            f.write('\n' + '='*80 + '\n\n')
    # CSV
    import csv
    with open(csv_path, 'w', encoding='utf-8', newline='') as cf:
        writer = csv.DictWriter(cf, fieldnames=['filename','filepath','sender','recipient','char_count','formatted_text'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f'Wrote preview: {txt_path.resolve()}')
    print(f'Wrote sample CSV: {csv_path.resolve()}')

if __name__ == '__main__':
    main()
