{
  description = "optional description";

  nixConfig.bash-prompt = ''\033[1;32m\[[nix-develop:\[\033[36m\]\w\[\033[32m\]]$\033[0m '';

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/23.11-pre";
    whacked-setup = {
      url = "github:whacked/setup/2e4dddabe0d82671305c3fa0cf97822664963936";
      flake = false;
    };
  };
  outputs = { self, nixpkgs, flake-utils, whacked-setup }:
    flake-utils.lib.eachDefaultSystem
    (system:
    let
      pkgs = nixpkgs.legacyPackages.${system};
      whacked-helpers = import (whacked-setup + /nix/flake-helpers.nix) { inherit pkgs; };
      python3Packages_jsonschema2db = import ./jsonschema2db.nix { inherit pkgs; };
      python3Packages_pglast = pkgs.python3.pkgs.buildPythonPackage rec {
        pname = "pglast";
        version = "1.17";
        src = pkgs.fetchPypi {
          inherit pname version;
          sha256 = "1ygmwf39wzx6qzm06zzf8xv6mnq45pvg52mpbl5glb7pln6b6y99";
        };
        checkInputs = [ ];
      };
    in {
      devShell = whacked-helpers.mkShell {
        flakeFile = __curPos.file;  # used to forward current file to echo-shortcuts
        includeScripts = [
          (whacked-setup + /bash/node_shortcuts.sh)
        ];
      } {
        buildInputs = [
          pkgs.jq
          pkgs.jsonnet
          pkgs.nodejs
          pkgs.python3Packages.coloredlogs
          pkgs.python3Packages.icecream
          pkgs.python3Packages.ipython
          pkgs.python3Packages.jsonnet
          pkgs.python3Packages.jsonschema
          pkgs.python3Packages.pyaml
          pkgs.python3Packages.pydantic
          pkgs.python3Packages.psycopg2
          pkgs.python3Packages.sqlalchemy
          python3Packages_pglast
          python3Packages_jsonschema2db
          pkgs.watchexec
        ];

        shellHook = ''
          unset name shellHook
          activate-node-env

          alias jsonnet2sql='python jsonnet2sql.py'
        '';  # join strings with +
      };
    }
  );
}
