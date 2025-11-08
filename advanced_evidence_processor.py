#!/usr/bin/env python3
"""
Advanced Evidence Processor - Handles multimedia and document extraction
Case: FDSJ-739-24 - Comprehensive Multi-Format Evidence Processing
"""

import os
import csv
import subprocess
import logging
from datetime import datetime
from pathlib import Path
import re
from typing import Dict, Tuple

# Attempt to import necessary libraries (user must install them)
try:
    from pydub import AudioSegment
    import moviepy.editor as mp
    import speech_recognition as sr
    from pdfminer.high_level import extract_text_from_file
    from docx import Document
    ADVANCED_LIBS_AVAILABLE = True
except ImportError:
    ADVANCED_LIBS_AVAILABLE = False
    
# Import config settings (assuming config/settings.py is present)
try:
    from config.settings import relevance_codes, priority_weights, multimedia_extensions
except ImportError:
    # Use fallback defaults if config is missing
    multimedia_extensions = ['.pdf', '.mp4', '.mp3', '.docx']
    relevance_codes = {'GENERAL': ['harper']}
    priority_weights = {'GENERAL': 1}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedEvidenceProcessor:
    
    def __init__(self):
        self.output_folder = Path("output")
        self.input_folder = Path("custody_screenshots_smart_renamed")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_filename = self.output_folder / f"harper_advanced_results_{self.timestamp}.csv"
        
        if not ADVANCED_LIBS_AVAILABLE:
            logger.warning("Missing libraries (pydub, moviepy, speech_recognition, pdfminer.six, python-docx). Multimedia processing disabled.")

    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file using PDFMiner."""
        try:
            return extract_text_from_file(file_path)
        except Exception as e:
            logger.error(f"PDF extraction failed for {file_path}: {e}")
            return ""

    def extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file using python-docx."""
        try:
            document = Document(file_path)
            return "\n".join([paragraph.text for paragraph in document.paragraphs])
        except Exception as e:
            logger.error(f"DOCX extraction failed for {file_path}: {e}")
            return ""

    def transcribe_audio(self, file_path: Path) -> str:
        """Transcribe audio/video file using speech_recognition."""
        
        if file_path.suffix.lower() in ['.mp4', '.mov']:
            # 1. Convert video to audio (MP4, MOV -> MP3)
            logger.info(f"Converting video to audio: {file_path.name}")
            temp_audio = Path(self.output_folder / f"temp_{file_path.stem}.mp3")
            try:
                clip = mp.VideoFileClip(str(file_path))
                clip.audio.write_audiofile(str(temp_audio))
                clip.close()
            except Exception as e:
                logger.error(f"Video to audio conversion failed: {e}")
                return ""
            audio_path = temp_audio
        else:
            audio_path = file_path

        # 2. Transcribe audio file
        r = sr.Recognizer()
        text = ""
        try:
            # Convert to WAV for better recognition compatibility
            if audio_path.suffix.lower() != '.wav':
                audio = AudioSegment.from_file(audio_path)
                wav_path = Path(self.output_folder / f"temp_{audio_path.stem}.wav")
                audio.export(wav_path, format="wav")
                
                with sr.AudioFile(str(wav_path)) as source:
                    audio_data = r.record(source)
                    text = r.recognize_google(audio_data)
                os.remove(wav_path)
            
            elif audio_path.suffix.lower() == '.wav':
                with sr.AudioFile(str(audio_path)) as source:
                    audio_data = r.record(source)
                    text = r.recognize_google(audio_data)
            
        except sr.UnknownValueError:
            text = "[TRANSCRIPTION_FAILED: Could not understand audio]"
            logger.warning(f"Transcription failed for {file_path}: Audio unclear")
        except Exception as e:
            logger.error(f"Transcription error for {file_path}: {e}")
        finally:
            if 'temp_audio' in locals() and os.path.exists(temp_audio):
                os.remove(temp_audio)
                
        return text

    def categorize_content(self, text: str) -> Tuple[str, str]:
        """Categorize content with priority scoring."""
        text_lower = text.lower()
        
        best_priority = 1
        best_category = 'GENERAL_EVIDENCE'
        
        for category, keywords in relevance_codes.items():
            if any(keyword in text_lower for keyword in keywords):
                priority = priority_weights.get(category, 1)
                if priority > best_priority:
                    best_priority = priority
                    best_category = category
        
        return best_category, self.get_priority_label(best_priority)

    def get_priority_label(self, score: int) -> str:
        if score >= 9:
            return "CRITICAL"
        elif score >= 7:
            return "HIGH"
        elif score >= 5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def process_all_advanced_files(self):
        """Find and process all multimedia/document files."""
        if not ADVANCED_LIBS_AVAILABLE:
            logger.error("Cannot run advanced processing due to missing libraries.")
            return

        all_files = []
        for ext in multimedia_extensions:
            all_files.extend(self.input_folder.rglob(f"*{ext}"))

        with open(self.csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['filename', 'file_path', 'file_type', 'date_extracted', 'text_content', 'text_length', 'priority', 'categories', 'processing_timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            logger.info(f"Found {len(all_files)} advanced files to process.")

            for file_path in all_files:
                file_type = file_path.suffix.lower()
                text_content = ""
                
                if file_type == '.pdf':
                    text_content = self.extract_text_from_pdf(file_path)
                elif file_type == '.docx':
                    text_content = self.extract_text_from_docx(file_path)
                elif file_type in ['.mp4', '.mov', '.mp3', '.wav']:
                    text_content = self.transcribe_audio(file_path)
                
                if text_content:
                    categories, priority = self.categorize_content(text_content)
                    
                    # Try to extract date from filename
                    date_match = re.search(r'(\d{8})', file_path.name)
                    date_extracted = date_match.group(1) if date_match else "unknown"

                    writer.writerow({
                        'filename': file_path.name,
                        'file_path': str(file_path),
                        'file_type': file_type,
                        'date_extracted': date_extracted,
                        'text_content': text_content[:1000].replace('\n', ' '),
                        'text_length': len(text_content),
                        'priority': priority,
                        'categories': categories,
                        'processing_timestamp': datetime.now().isoformat()
                    })
                    logger.info(f"✓ Processed {file_path.name} ({priority} | {categories})")
                else:
                    logger.warning(f"Skipped {file_path.name} - No content extracted.")

        logger.info(f"Advanced evidence processing complete. Results saved to {self.csv_filename.name}")

if __name__ == "__main__":
    if not ADVANCED_LIBS_AVAILABLE:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!!  CRITICAL ERROR: MISSING PYTHON LIBRARIES  !!!")
        print("!!!  Please install: moviepy, pydub, speech_recognition,     !!!")
        print("!!!  pdfminer.six, python-docx (or install all with pip)     !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        processor = AdvancedEvidenceProcessor()
        processor.process_all_advanced_files()