with import <nixpkgs> {};

let
in stdenv.mkDerivation rec {
  name = "BorderScreama";
  env = buildEnv {
    name = name;
    paths = buildInputs;
  };
  buildInputs = [
    python38Full
    python38Packages.coloredlogs
    python38Packages.jsonschema
    python38Packages.pyaml
    python38Packages.pydantic
    nodejs
    watchexec
  ];

  shellHook = ''
    export PATH=$PATH:$(npm bin)
    unset name
  '';
}
