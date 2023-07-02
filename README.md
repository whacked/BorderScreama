highly explorative / experimental code around schema generation/sync across program boundaries

# usage

activate development environment using `nix develop`

# examples

## jsonnet -> json schema -> pydantic/sqlmodel

see examples/sqlmodel-generator

`python main.py` runs an example of sqlmodels generated from schemas declared in `generators`
