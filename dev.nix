{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/nixos-23.11.tar.gz") {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # System-level dependencies
    tesseract5
    ffmpeg

    # Python environment with consolidated packages
    (python311.withPackages (ps: with ps; [
      # Core environment
      pip

      # Evidence Processing, Data Analysis & Visualization
      streamlit
      pytesseract
      Pillow
      pandas
      opencv
      numpy
      python-dateutil
      tqdm
      openpyxl
      PyPDF2
      python-docx
      moviepy
      SpeechRecognition
      psutil
      reportlab
      matplotlib
      seaborn

      # AI and Machine Learning
      google-genai
      scikit-learn
      langchain
    ]))
  ];
}
