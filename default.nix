with import <nixpkgs> {};

let
  python39Packages_jsonschema2db = import ./jsonschema2db.nix;
  python39Packages_pglast = python39.pkgs.buildPythonPackage rec {
    pname = "pglast";
    version = "1.17";
    src = python39.pkgs.fetchPypi {
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
    python39Packages.coloredlogs
    python39Packages.icecream
    python39Packages.ipython
    python39Packages.jsonnet
    python39Packages.jsonschema
    python39Packages.pyaml
    python39Packages.pydantic
    python39Packages.psycopg2
    python39Packages.sqlalchemy
    python39Packages_pglast
    python39Packages_jsonschema2db
    watchexec
  ];

  shellHook = ''
    export PATH=$PATH:$(npm bin)
    unset name

    alias jsonnet2sql='python jsonnet2sql.py'
    cat ${__curPos.file} | grep '^[[:space:]]*\(function\|alias\).*'
  '';
}
