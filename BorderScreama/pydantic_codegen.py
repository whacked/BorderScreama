import sys
import os.path as _p
import json
from pathlib import Path
from datamodel_code_generator import InputFileType, generate
from dataclasses import dataclass
from typing import List
import tempfile


def json_schema_to_pydantic(schema_path: str):
    temp_output_dir = tempfile.TemporaryDirectory()
    sys.stderr.write(f'[DEBUG] check your dir in {temp_output_dir}\n')

    input_schema_dir = _p.split(schema_path)[0]
    with open(schema_path) as ifile:
        json_schema = json.load(ifile)
    properties = json_schema['properties']
    keep_properties = {}
    foreign_keys = {}
    for key, prop in properties.items():
        # foreign table
        if prop.get('$ref'):
            ref_file = prop['$ref']
            with open(_p.join(input_schema_dir, ref_file)) as ifile:
                ref_schema = json.load(ifile)

            foreign_table_name = ref_schema['title']

            @dataclass
            class Table:
                name = foreign_table_name
                back_populates = f'{json_schema["title"].lower()}s'
            foreign_keys[key] = Table
        else:
            keep_properties[key] = prop
    json_schema['properties'] = keep_properties
    output_filename = json_schema['title'] + '.py'
    # output = Path(_p.join(output_dir, output_filename))
    output = Path(_p.join(temp_output_dir.name, output_filename))
    generate(
        json.dumps(json_schema),
        input_file_type=InputFileType.JsonSchema,
        input_filename=schema_path,
        output=output,
    )
    model: str = output.read_text()

    temp_output_dir.cleanup()

    out_lines = []
    for line in str(model).splitlines():
        out_lines.append(line)
        if line.startswith('from __future__'):
            for (key, table) in foreign_keys.items():
                out_lines.append(
                    f'from {table.name} import {table.name}'
                )
    for (key, table) in foreign_keys.items():
        out_lines.append(
            f'    {key}: Optional[{table.name}] = None'
        )
    return '\n'.join(out_lines)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--schema-path')
    parser.add_argument('--output-path')

    args = parser.parse_args()

    if not args.schema_path:
        raise ValueError('schema paths required')

    output_code = json_schema_to_pydantic(args.schema_path)
    if args.output_path:
        with open(args.output_path, 'w') as ofile:
            ofile.write(output_code)
    else:
        sys.stdout.write(output_code)
    
