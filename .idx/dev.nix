{ pkgs, ... }: {
  # Let Nix handle shader compilation for Flutter
  # hardware.opengl.enable = true;

  # Tell Nix to use the correct C++ stdlib for Flutter
  # NIXOS_CC_WRAPPER_TARGET_HOST_x86_64_unknown_linux_gnu = "c++";

  # And to use the correct linker
  # NIXOS_LD_WRAPPER_TARGET_HOST_x86_64_unknown_linux_gnu = "ld";

  # Enter a shell with the flutter sdk available
  channel = "stable-23.11"; # Or "unstable"
  packages = [
    pkgs.python311
    pkgs.python311Packages.pip
    # Pytesseract dependency
    pkgs.tesseract
  ];
  idx = {
    # Search for extensions in the VS Code Marketplace.
    # See https://open-vsx.org/ for available extensions.
    extensions = [
      "ms-python.python"
      "ms-toolsai.jupyter"
    ];

    # Enable previews
    previews = {
      enable = true;
      previews = {
        web = {
          command = ["streamlit", "run", "app.py", "--server.port", "$PORT", "--server.address", "0.0.0.0", "--server.enableCORS", "false"];
          manager = "web";
        };
      };
    };

    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        # Example: install JS dependencies from NPM
        install-dependencies = "pip install -r requirements.txt";
      };
      # Runs when the workspace is (re)started
      onStart = {
        # Example: start a background task to watch and re-build backend code
        # watch-backend = "npm run watch-backend";
      };
    };
  };
}
