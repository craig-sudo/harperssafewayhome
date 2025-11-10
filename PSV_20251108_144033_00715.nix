{ pkgs, ... }:

let
  requirements = pkgs.runCommand "python-requirements" { } ''
    ${pkgs.python3.pkgs.pip}/bin/pip install -r ${./requirements.txt} --prefix=$out
  '';
in
pkgs.python3.pkgs.buildPythonPackage {
  name = "harper-dependencies";
  src = requirements;
  format = "other";
  propagatedBuildInputs = (with pkgs.python3.pkgs; [
    # List any packages that have system-level dependencies here if needed
    # For example: opencv4
  ]);
}