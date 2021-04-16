{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = [
    pkgs.python38Full
    pkgs.postgresql
    pkgs.glibcLocales
    pkgs.lsb-release
  ];

  nativeBuildInputs = [
    ~/setup/bash/nix_shortcuts.sh
    ~/setup/bash/shell_shortcuts.sh
    ~/setup/bash/postgresql_shortcuts.sh
  ];

  shellHook = ''
    export VIRTUAL_ENV=''${VIRTUAL_ENV:-venv}
    initialize-venv() {
        pip install icecream ipython
        pip install frictionless frictionless[sql] tableschema tableschema-sql psycopg2 pydantic sqlparse ddlparse
    }

    ensure-venv initialize-venv
  '';
}
