    { description = "Pro Se Veritas Development Environment";

      # Which nixpkgs channel to use.
      channel = "stable-23.11";

      inputs.nixpkgs.url = "github.com/NixOS/nixpkgs/nixos-${channel}";
      
      # Use the stable python environment and load all dependencies using `withPackages`.
      # This is a more robust way to handle large groups of Python dependencies in Nix.
      packages = [
        # Core System Dependencies
        pkgs.tesseract5
        
        # All Python Packages (consolidated)
        (pkgs.python311.withPackages (python-pkgs: with python-pkgs; [
          # Core Environment
          pip
          
          # Evidence Processing & Data Analysis
          streamlit
          pytesseract
          Pillow
          pandas
          opencv-python
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
          
          # Advanced AI and Legal Analysis
          google-genai
          scikit-learn
          
          # Note: 'firebase-admin' is removed here to resolve the original build error.
          # It can be added back after confirming the correct Nix package name.
        ]))
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
          "google.gemini-cli-vscode-ide-companion"
          "google.geminicodeassist"
          "googlecloudtools.cloudcode"
          "ms-python.debugpy"
          "ms-toolsai.jupyter-keymap"
          "ms-toolsai.jupyter-renderers"
          "ms-toolsai.vscode-jupyter-cell-tags"
          "ms-toolsai.vscode-jupyter-slideshow"
          "mutable-ai.mutable-ai"
          "njpwerner.autodocstring"
          "vitest.explorer"
        ];
        
        # Enable previews
        # This 'previews' block is a direct child of the 'idx' block.
        previews = { 
          enable = true;
          previews = {
            web = {
              command = [
                "python3"
                "-m"
                "streamlit"
                "run"
                "streamlit_app.py"
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
    {
      description = "Pro Se Veritas Development Environment";

      # Which nixpkgs channel to use.
      channel = "stable-23.11";
      
      inputs.nixpkgs.url = "github.com/NixOS/nixpkgs/nixos-${self.channel}";
      
      # Use the stable python environment and load all dependencies using `withPackages`.
      # This is a more robust way to handle large groups of Python dependencies in Nix.
      packages = [
        # Core System Dependencies
        pkgs.tesseract5
        
        # All Python Packages (consolidated)
        (pkgs.python311.withPackages (python-pkgs: with python-pkgs; [
          # Core Environment
          pip
          
          # Evidence Processing & Data Analysis
          streamlit
          pytesseract
          Pillow
          pandas
          opencv-python
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
          
          # Advanced AI and Legal Analysis
          google-genai
          scikit-learn
          
          # Note: 'firebase-admin' is removed here to resolve the original build error.
          # It can be added back after confirming the correct Nix package name.
        ]))
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
          "google.gemini-cli-vscode-ide-companion"
          "google.geminicodeassist"
          "googlecloudtools.cloudcode"
          "ms-python.debugpy"
          "ms-toolsai.jupyter-keymap"
          "ms-toolsai.jupyter-renderers"
          "ms-toolsai.vscode-jupyter-cell-tags"
          "ms-toolsai.vscode-jupyter-slideshow"
          "mutable-ai.mutable-ai"
          "njpwerner.autodocstring"
          "vitest.explorer"
        ];
        
        # Enable previews
        # This 'previews' block is a direct child of the 'idx' block.
        previews = { 
          enable = true;
          previews = {
            web = {
              command = [
                "python3"
                "-m"
                "streamlit"
                "run"
                "streamlit_app.py"
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