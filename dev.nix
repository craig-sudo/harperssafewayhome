{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/nixos-23.11.tar.gz") {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # System-level dependencies needed by Python packages
    tesseract
    ffmpeg

    # Python environment with packages declared directly
    (python3.withPackages (ps: with ps; [
      # Packages from requirements.txt
      streamlit
      pytesseract
      pillow
      pandas
      opencv
      numpy
      python-dateutil
      tqdm
      openpyxl
      pypdf2
      python-docx
      moviepy
      speechrecognition
      psutil
      reportlab
      matplotlib
      seaborn
      google-genai
      scikitlearn
      langchain
    ]))
  ];
}