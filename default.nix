with import <nixpkgs> {};

let
in stdenv.mkDerivation rec {
  name = "BorderScreama";
  env = buildEnv {
    name = name;
    paths = buildInputs;
  };
  buildInputs = [
    python37Full
    python37Packages.coloredlogs
    python37Packages.jsonschema
    python37Packages.pyaml
    python37Packages.pydantic
    nodejs
    watchexec
  ];

  shellHook = ''
    export PATH=$PATH:$(npm bin)
    unset name
  '';
}

