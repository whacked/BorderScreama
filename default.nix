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
    python37Packages.jsonschema
    nodejs
  ];

  shellHook = ''
  '';
}

