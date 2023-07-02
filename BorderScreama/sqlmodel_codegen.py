import sys
import os
import os.path as _p
import json
from pathlib import Path
from datamodel_code_generator import InputFileType, generate
from dataclasses import dataclass
from typing import List
import tempfile


def load_schema(schema_path: str):
    with open(schema_path) as ifile:
        json_schema = json.load(ifile)
    return json_schema

def json_schema_to_sqlmodel(schema_paths: List[str]):
    NEWLINE = '\n'
    header_blocks = [
        'from typing import List, Optional',
        'from sqlmodel import Field, Relationship, Session, SQLModel, create_engine',
    ]
    output_code_blocks = []

    # WARN: only works for 2 tables
    join_tables = []

    temp_output_dir = tempfile.TemporaryDirectory()
    sys.stderr.write(f'[DEBUG] check your dir in {temp_output_dir}\n')

    for schema_path in schema_paths:
        input_schema_dir = _p.split(schema_path)[0]
        with open(schema_path) as ifile:
            json_schema = json.load(ifile)
        properties = json_schema['properties']
        keep_properties = {}
        foreign_keys = {}
        for key, prop in properties.items():
            # foreign table
            if prop.get('type') == 'array' and prop.get('items', {}).get('$ref'):
                ref_file = prop['items']['$ref']
                if ref_file == '#':  # self
                    ref_schema = json_schema.copy()
                    # prevent circular reference from the self import
                    ref_schema['properties'][key] = {}
                else:
                    ref_schema = load_schema(_p.join(input_schema_dir, ref_file))

                foreign_table_name = ref_schema['title'].lower()

                @dataclass
                class Table:
                    model_name = json_schema["title"]
                    name = foreign_table_name
                    back_populates = f'{json_schema["title"].lower()}s'
                foreign_keys[key] = Table
                join_tables.append(Table)

                # if ref_file == '#':
                #     join_tables.append(Table)  # again for self join
                
            elif prop.get('$ref'):
                ref_schema = load_schema(_p.join(input_schema_dir, prop['$ref']))
                foreign_table_name = ref_schema['title'].lower()
                @dataclass
                class Table:
                    model_name = ref_schema["title"]
                    name = foreign_table_name
                foreign_keys[key] = Table
            elif prop == {}:
                keep_properties[key] = {
                    'description': 'serialized JSON (from any type in schema)',
                    'type': 'string',
                }
            else:
                keep_properties[key] = prop
        json_schema['properties'] = keep_properties
        output_filename = json_schema['title'] + '.py'
        output = Path(_p.join(temp_output_dir.name, output_filename))
        generate(
            json.dumps(json_schema),
            input_file_type=InputFileType.JsonSchema,
            input_filename=schema_path,
            output=output,
        )
        model: str = output.read_text()
        output_code_blocks.append(model)
        foreign_models = []
        for key, table in foreign_keys.items():
            if hasattr(table, 'back_populates'):
                foreign_models.append(f'    {key}: List["{table.name}"] = Relationship(back_populates="{table.back_populates}", link_model=%(link_model)s)')
            else:
                foreign_models.append(f'    {key}_id: Optional[int] = Field(default=None, foreign_key="{table.name}.id")')
        output_code_blocks.append('\n'.join(foreign_models))
    
    temp_output_dir.cleanup()

    # WARN FIXME HACK: this only works for a single, 2-table join
    if len(join_tables) == 2:
        join_table_name = ''.join(list([
            table.model_name for table in
            sorted(join_tables, key=lambda a: a.name)])) + 'Link'
        fields = [
            f'\n    {table.name.lower()}_id: Optional[int] = Field(default=None, foreign_key="{table.name.lower()}.id", primary_key=True)'
            for table in join_tables
        ]
        link_class_code = f'\n\nclass {join_table_name}(SQLModel, table=True):{"".join(fields)}'
    else:
        join_table_name = None
        link_class_code = ''
    header_blocks.append(link_class_code + '\n\n')

    class_code = []
    for class_block in output_code_blocks:
        class_lines = []
        for line in class_block.splitlines():
            if line.startswith(('from ', 'import ')):
                continue
            elif line.startswith('    id:'):
                class_lines.append(line.replace('= None', '= Field(default=None, primary_key=True)'))
                continue
            elif line == '':
                continue
            elif line.endswith('(BaseModel):'):
                class_lines.append(line.replace('(BaseModel):', '(SQLModel, table=True):'))
                continue
            class_lines.append(line)
        class_code.append(('\n'.join(class_lines)) % dict(
            link_model=join_table_name,
        ) + '\n')

    return '\n'.join(header_blocks) + '\n'.join(class_code)


if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--schema-paths', nargs='+')
    parser.add_argument('--output-path')

    args = parser.parse_args()

    if not args.schema_paths:
        raise ValueError('schema paths required')

    output_code = json_schema_to_sqlmodel(args.schema_paths)
    if args.output_path:
        with open(args.output_path, 'w') as ofile:
            ofile.write(output_code)
    else:
        sys.stdout.write(output_code)
    
