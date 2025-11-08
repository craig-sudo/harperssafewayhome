# config/settings.py

# ============================================================================
# TESSERACT OCR CONFIGURATION
# ============================================================================

# Path to Tesseract executable (Required for Windows)
tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Tesseract configuration string
tesseract_config = '--oem 3 --psm 6 -l eng' 

# Minimum OCR confidence score required for 'SUCCESS' status
min_ocr_confidence = 70.0 

# ============================================================================
# IMAGE PREPROCESSING SETTINGS
# ============================================================================
use_binary_threshold = True
binary_threshold = 130 

# ============================================================================
# LEGAL CATEGORIES (Used by secure_evidence_processor.py)
# ============================================================================

relevance_codes = {
    'CRIMINAL_CONDUCT': ['assault', 'police', 'court', 'december 9', 'charged'],
    'ENDANGERMENT': ['sick', 'doctor', 'injury', 'danger', 'harper', 'welfare'],
    'NON_COMPLIANCE': ['blocked', 'refused', 'contempt', 'custody violation'],
    'SUBSTANCE_ABUSE': ['meth', 'drug', 'cocaine', 'pills', 'substance', 'alcohol'],
    'FINANCIAL_ISSUE': ['money', 'support', 'payment', 'bank', 'owe', 'rent'],
    'REVIEW_REQUIRED': []
}

priority_weights = {
    'CRIMINAL_CONDUCT': 10, 
    'ENDANGERMENT': 9, 
    'SUBSTANCE_ABUSE': 8,
    'NON_COMPLIANCE': 7,
    'FINANCIAL_ISSUE': 5,
    'REVIEW_REQUIRED': 1
}

# ============================================================================
# FILE PROCESSING SETTINGS
# ============================================================================
image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
multimedia_extensions = ['.pdf', '.mp4', '.mov', '.mp3', '.wav', '.docx']
output_encoding = 'utf-8'