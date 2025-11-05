nix
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; 

  # Use https://search.nixos.org/packages to find packages
  packages = [
    # Core Python environment
    pkgs.python311
    pkgs.python311Packages.pip
    
    # OCR and Tesseract dependency
    pkgs.tesseract5
    
    # All packages from requirements.txt, installed via Nix (Hyphens converted to underscores):
    pkgs.python311Packages.streamlit
    pkgs.python311Packages.firebase_admin         # FIXED: firebase-admin -> firebase_admin
    pkgs.python311Packages.pytesseract
    pkgs.python311Packages.Pillow
    pkgs.python311Packages.pandas
    pkgs.python311Packages.opencv_python         # FIXED: opencv-python -> opencv_python
    pkgs.python311Packages.numpy
    pkgs.python311Packages.python_dateutil       # FIXED: python-dateutil -> python_dateutil
    pkgs.python311Packages.tqdm
    pkgs.python311Packages.openpyxl
    pkgs.python311Packages.PyPDF2
    pkgs.python311Packages.python_docx           # FIXED: python-docx -> python_docx
    pkgs.python311Packages.moviepy
    pkgs.python311Packages.SpeechRecognition
    pkgs.python311Packages.psutil
    pkgs.python311Packages.reportlab
    pkgs.python311Packages.matplotlib
    pkgs.python311Packages.seaborn
    
    # New dependencies for Advanced AI and Legal Analysis
    pkgs.python311Packages.google_genai          # FIXED: google-genai -> google_genai
    pkgs.python311Packages.scikit_learn          # FIXED: scikit-learn -> scikit_learn
  ];

  # Sets environment variables in the workspace
  env = {
    # Permanently sets the API key for the Pro Se Veritas AI features
    GEMINI_API_KEY = "AIzaSyCMbuJT7r6HE1vX0tWANYIX71QFj5_adTI";
  };

  idx = {
    # Search for the extensions you want on https://open-vsx.org/
    extensions = [
      "ms-python.python"
      "ms-toolsai.jupyter"
    ];
    
    # Enable previews
    previews = { 
      enable = true;
      previews = {
        web = {
          command = [
            "python3"
            "-m"
            "streamlit"
            "run"
            "app.py"
            "--server.port"
            "$PORT"
            "--server.address"
            "0.0.0.0"
            "--server.enableCORS"
            "false"
          ];
          manager = "web";
        };
      };
    };
  };
}

