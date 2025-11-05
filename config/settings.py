
# config/settings.py

# Tesseract OCR configuration
tesseract_config = "--psm 6"
min_ocr_confidence = 80
tesseract_cmd = None  # Set to your Tesseract path if not in system PATH, e.g., r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# File extensions to process
image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']

# Relevance codes for content categorization
relevance_codes = {
    'CRIMINAL_CONDUCT': ['drug', 'illegal', 'stole', 'theft'],
    'ENDANGERMENT': ['danger', 'unsafe', 'neglect', 'abuse'],
    'NON_COMPLIANCE': ['court order', 'custody agreement', 'violation'],
    'FINANCIAL_IMPACT': ['rent', 'bill', 'pay', 'money'],
    'USER_COMMITMENT': ['promise', 'agree', 'commit'],
    'COMMUNICATION': ['text', 'message', 'email', 'call'],
    'REVIEW_REQUIRED': []
}

# CSV fields for the output file
csv_fields = [
    'File_Name',
    'File_Integrity_Hash',
    'Date_Time_Approx',
    'Sender',
    'Recipient',
    'Key_Factual_Statement',
    'Relevance_Code',
    'Processing_Status',
    'Confidence_Score',
    'Legal_Priority',
    'File_Size_Bytes',
    'Processing_Session',
    'Processed_DateTime'
]
