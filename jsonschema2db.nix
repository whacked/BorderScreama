{ pkgs ? import <nixpkgs> }:

let
  change_case = pkgs.python3.pkgs.buildPythonPackage rec {
    pname = "change_case";
    version = "0.5.2";
    
    src = pkgs.python3.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "1nb3w2qjx8zl327vfssqznl33r70m3i11fm1snhvmh4fi1far5k0";
    };
  };

  jsonschema2db = pkgs.python3.pkgs.buildPythonPackage rec {
    pname = "JSONSchema2DB";
    version = "1.0.1";

    src = pkgs.python3.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "1857bzx77491wva6dmixm9x8pqm7kn7l29fpcdvr07niid5jh0lp";
    };

    # hack the upstream setup.py file to accept newer dependencies
    # latest versions as of this commit:
    # iso8601      0.1.14
    # change_case  0.5.2
    # psycopg2     2.8.6
    preConfigure = ''
        if [ ! -e setup.py.orig ]; then mv setup.py setup.py.orig; fi
        cat setup.py.orig |
          sed -e 's/\(iso8601\|psycopg2\)==/\1>=/' |
          cat > setup.py
      '';

    propagatedBuildInputs = [
      pkgs.python3.pkgs.iso8601
      pkgs.python3.pkgs.psycopg2
      change_case
    ];

    meta = {
      homepage = "https://github.com/better/jsonschema2db";
    };
  };
in
  pkgs.python3.withPackages (ps: [jsonschema2db])
