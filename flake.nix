{
  description = "A Nix-flake-based Python development environment";

  inputs.nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.1.*.tar.gz";

  outputs =
    { self, nixpkgs }:
    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forEachSupportedSystem =
        f:
        nixpkgs.lib.genAttrs supportedSystems (
          system:
          f {
            pkgs = import nixpkgs { inherit system; };
          }
        );
    in
    {
      devShells = forEachSupportedSystem (
        { pkgs }:
        {
          default = pkgs.mkShell {
            venvDir = ".venv";
            packages =
              with pkgs; [
                python311

                xcb-util-cursor
                xorg.libxcb
                #libxcb-cursor

                # qt5.qtbase
                qt6.qtbase

                python311Packages.pyqt5

                (python311.pkgs.matplotlib.override { enableQt = true; })
              ]
              ++ (with pkgs.python311Packages; [
                pip
                venvShellHook

                # security
                python-dotenv

                # REPL
                ipykernel

                # GUI
                pyqt6

                requests
                networkx
                # matplotlib
                bokeh
              ]);

            shellHook = "python -m ipykernel install --user";
          };
        }
      );
    };
}
