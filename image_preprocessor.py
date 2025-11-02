# image_preprocessor.py
# Functions to enhance image quality specifically for Tesseract OCR

from PIL import Image, ImageEnhance, ImageOps
import cv2
import numpy as np
import os

def preprocess_image_for_ocr(image_path):
    """
    Military-grade image preprocessing for messaging app screenshots
    Handles compression artifacts, low resolution, and complex backgrounds
    """
    try:
        # 1. Load image and convert to grayscale
        img = cv2.imread(image_path)
        if img is None:
            print(f"Warning: Could not load image {image_path}")
            return image_path
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. Deskew (Straighten rotated images)
        coords = np.column_stack(np.where(gray > 0))
        if len(coords) == 0:
            print(f"Warning: No content found in image {image_path}")
            return image_path
            
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        # Only apply rotation if angle is significant (> 1 degree)
        if abs(angle) > 1:
            (h, w) = img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        else:
            rotated = gray

        # 3. ADVANCED: Otsu's Binarization (better than adaptive thresholding)
        # Automatically determines optimal threshold for varying contrast
        # THRESH_BINARY_INV = white background, black text (Tesseract preference)
        _, thresh = cv2.threshold(rotated, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # 4. MILITARY-GRADE: Morphological Operations to fix compression artifacts
        # Create kernel for morphological operations
        kernel = np.ones((3, 3), np.uint8)
        
        # CLOSING operation (dilation followed by erosion)
        # - Fills small holes in text (JPEG compression damage)
        # - Connects broken letter parts
        # - Smooths rough edges from compression artifacts
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # 5. Additional cleanup: Remove small noise blobs
        # Find contours and remove very small ones (noise)
        contours, _ = cv2.findContours(processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 10:  # Remove tiny noise spots
                cv2.fillPoly(processed, [contour], 0)

        # Save the temporary processed image (Tesseract needs a file path)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        temp_path = f"temp_military_processed_{base_name}_ocr.png"
        cv2.imwrite(temp_path, processed)
        
        return temp_path

    except Exception as e:
        print(f"Military-grade preprocessing failed for {image_path}: {e}")
        return image_path  # Return original path if preprocessing fails


def preprocess_messaging_app_screenshot(image_path):
    """
    Specialized preprocessing for heavily compressed messaging app screenshots
    Targets iMessage, WhatsApp, Facebook Messenger compression artifacts
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return image_path
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 1. Aggressive denoising for JPEG compression artifacts
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # 2. Enhance contrast before binarization
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # 3. Multi-stage binarization for complex backgrounds
        # First pass: Otsu's for main text
        _, binary1 = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Second pass: Adaptive for remaining text
        binary2 = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # Combine both approaches
        combined = cv2.bitwise_or(binary1, binary2)
        
        # 4. Aggressive morphology for messaging apps
        # Larger kernel for heavily compressed text
        kernel_large = np.ones((5, 5), np.uint8)
        kernel_small = np.ones((2, 2), np.uint8)
        
        # Opening to remove noise, then closing to connect text
        opened = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel_small)
        processed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel_large)
        
        # 5. Final cleanup for messaging app UI elements
        # Remove horizontal/vertical lines (UI elements)
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
        
        horizontal_lines = cv2.morphologyEx(processed, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_lines = cv2.morphologyEx(processed, cv2.MORPH_OPEN, vertical_kernel)
        
        # Remove detected UI lines from the image
        processed = cv2.subtract(processed, horizontal_lines)
        processed = cv2.subtract(processed, vertical_lines)
        
        # Save result
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        temp_path = f"temp_messaging_processed_{base_name}_ocr.png"
        cv2.imwrite(temp_path, processed)
        
        return temp_path
        
    except Exception as e:
        print(f"Messaging app preprocessing failed for {image_path}: {e}")
        return image_path


def preprocess_with_multiple_methods(image_path):
    """
    Tries multiple military-grade preprocessing approaches and returns all versions
    for OCR confidence comparison. Perfect for challenging messaging app screenshots.
    """
    methods = []
    
    try:
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        
        # Method 1: Military-grade (Otsu + Morphology)
        temp1 = preprocess_image_for_ocr(image_path)
        methods.append(('military_grade', temp1))
        
        # Method 2: Messaging app specialized
        temp2 = preprocess_messaging_app_screenshot(image_path)
        methods.append(('messaging_specialized', temp2))
        
        # Method 3: Conservative (for high-quality images)
        img = cv2.imread(image_path)
        if img is not None:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, conservative = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            temp3 = f"temp_{base_name}_conservative.png"
            cv2.imwrite(temp3, conservative)
            methods.append(('conservative', temp3))
        
        # Method 4: Extreme enhancement (for very poor quality)
        if img is not None:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Extreme contrast enhancement
            enhanced = cv2.convertScaleAbs(gray, alpha=2.5, beta=50)
            
            # Extreme denoising
            denoised = cv2.bilateralFilter(enhanced, 15, 80, 80)
            
            # Otsu with extreme morphology
            _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            kernel = np.ones((7, 7), np.uint8)
            extreme = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            temp4 = f"temp_{base_name}_extreme.png"
            cv2.imwrite(temp4, extreme)
            methods.append(('extreme_enhancement', temp4))
        
        return methods
        
    except Exception as e:
        print(f"Multi-method preprocessing failed for {image_path}: {e}")
        return [('original', image_path)]


def cleanup_temp_files(temp_path, original_path):
    """
    Safely removes temporary preprocessing files.
    """
    try:
        if temp_path != original_path and os.path.exists(temp_path):
            os.remove(temp_path)
            # Also clean up any other temp files from multi-method processing
            base_name = os.path.splitext(os.path.basename(original_path))[0]
            for method_file in [f"temp_{base_name}_method1.png", f"temp_{base_name}_method2.png", f"temp_{base_name}_method3.png"]:
                if os.path.exists(method_file):
                    os.remove(method_file)
    except Exception as e:
        print(f"Warning: Could not clean up temp file {temp_path}: {e}")


def enhance_image_contrast(image_path):
    """
    Simple contrast enhancement using PIL for screenshots with poor contrast.
    """
    try:
        with Image.open(image_path) as img:
            # Convert to grayscale
            if img.mode != 'L':
                img = img.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(img)
            enhanced = enhancer.enhance(2.0)  # Increase contrast by 2x
            
            # Save temporary enhanced image
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            temp_path = f"temp_enhanced_{base_name}.png"
            enhanced.save(temp_path)
            return temp_path
            
    except Exception as e:
        print(f"Contrast enhancement failed for {image_path}: {e}")
        return image_path