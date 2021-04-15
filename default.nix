with import <nixpkgs> {};

let
  jsonschema2db = import ./jsonschema2db.nix;
in stdenv.mkDerivation rec {
  name = "BorderScreama";
  env = buildEnv {
    name = name;
    paths = buildInputs;
  };
  buildInputs = [
    python38Packages.coloredlogs
    python38Packages.jsonschema
    python38Packages.pyaml
    python38Packages.pydantic
    nodejs
    watchexec
    jsonschema2db
  ];

  shellHook = ''
    export PATH=$PATH:$(npm bin)
    unset name
  '';
}
