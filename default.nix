with import <nixpkgs> {};

let
  python38Packages_jsonschema2db = import ./jsonschema2db.nix;
  python38Packages_pglast = python38.pkgs.buildPythonPackage rec {
    pname = "pglast";
    version = "1.17";
    src = python38.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "1ygmwf39wzx6qzm06zzf8xv6mnq45pvg52mpbl5glb7pln6b6y99";
    };
    checkInputs = [ ];
  };
in stdenv.mkDerivation rec {
  name = "BorderScreama";
  env = buildEnv {
    name = name;
    paths = buildInputs;
  };
  buildInputs = [
    jq
    jsonnet
    nodejs
    python38Packages.coloredlogs
    python38Packages.jsonnet
    python38Packages.jsonschema
    python38Packages.pyaml
    python38Packages.pydantic
    python38Packages_pglast
    python38Packages_jsonschema2db
    watchexec
  ];

  shellHook = ''
    export PATH=$PATH:$(npm bin)
    unset name

    alias jsonnet2sql='python jsonnet2sql.py'
    cat ${__curPos.file} | grep '^[[:space:]]*\(function\|alias\).*'
  '';
}
