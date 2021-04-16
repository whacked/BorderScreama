import sys
import json
from frictionless import Package
from BorderScreama.frictionless_capture import (
    get_generated_sql,
    load_schema,
    to_package_descriptor,
)
from typing import List
import sqlparse
from ddlparse import DdlParse
import re

def is_create(token: sqlparse.sql.Token):
    return (
        token.ttype == sqlparse.tokens.DDL
        and token.value == 'CREATE'
    )

def get_table_name(tokens: List[sqlparse.sql.Token]):
    table_name = next(
        token for token in tokens
        if isinstance(token, sqlparse.sql.Identifier))
    return str(table_name).strip('"')

def get_field_definitions(tokens: List[sqlparse.sql.Token]):
    table_name = next(
        token for token in tokens
        if isinstance(token, sqlparse.sql.Parenthesis))
    return [
        statement.strip()
        for statement in
        str(table_name).strip('()').split(',')
    ]

def discover_foreign_keys(source_table, definitions):
    foreign_keys = []
    for definition in definitions:
        if definition.upper().startswith('FOREIGN KEY'):
            matches = re.match(
                r'FOREIGN KEY\((?P<lkey>\w+)\)+\s+references\s+(?P<ftable>\w+)\s+\((?P<fkey>\w+)\)\s*',
                definition, re.IGNORECASE)
            if matches:
                mdict = matches.groupdict()
                reference_spec = {
                    'fields': mdict['fkey'],
                }
                if mdict['ftable'] == source_table:
                    # see the "articles.json" example from frictionless
                    reference_spec['resource'] = ""
                else:
                    reference_spec['resource'] = mdict['ftable']
                foreign_keys.append({
                    'fields': mdict['lkey'],
                    'reference': reference_spec,
                })
    return foreign_keys

def to_resource(name, schema):
    return {'name': name,
            'schema': schema}

def parse_sql_to_frictionless_resources(sql_input):
    resources = []
    statements = sqlparse.split(sql_input)
    for statement in statements:
        parsed = sqlparse.parse(statement)[0]
        if is_create(parsed.tokens[0]):
            table_name = get_table_name(parsed.tokens)
            
            table = DdlParse().parse(statement)
            schema = {'fields': []}
            for col, col_def in table.columns.items():
                schema['fields'].append({
                    'name': col,
                    'type': col_def.data_type.lower(),
                })
                if col_def.constraint == '':
                    continue
                elif col_def.constraint == 'PRIMARY KEY':
                    schema['primaryKey'] = col
                    schema['fields'][-1]['constraints'] = {
                        'required': True,
                    }
                else:
                    raise Exception(
                        'unhandled constraint: {}'.format(col_def.constraint))

            # can't use ddlparse for foreign keys now; parse extra:
            field_definitions = get_field_definitions(parsed.tokens)
            maybe_foreign_keys = discover_foreign_keys(
                table_name,
                field_definitions)
            if maybe_foreign_keys:
                schema['foreignKeys'] = maybe_foreign_keys

            resources.append(to_resource(table_name, schema))
    return resources

table = DdlParse().parse('''\
CREATE TABLE articles (
	id INTEGER NOT NULL, 
	parent INTEGER, 
	name TEXT, 
	current BOOLEAN, 
	rating NUMERIC, 
	created_date DATE, 
	created_time TIME, 
	created_datetime DATETIME, 
	location JSONB, 
	PRIMARY KEY (id), 
	FOREIGN KEY(parent) REFERENCES articles (id)
);
''')

if __name__ == '__main__':
    import sys
    sql_input = sys.stdin.read()

    ### EXAMPLE (modeled after articles.json, comments.json):
    # CREATE TABLE articles (
    #     id INTEGER NOT NULL, 
    #     parent INTEGER, 
    #     name TEXT, 
    #     current BOOLEAN, 
    #     rating NUMERIC, 
    #     created_date DATE, 
    #     created_time TIME, 
    #     created_datetime DATETIME, 
    #     location JSONB, 
    #     PRIMARY KEY (id), 
    #     FOREIGN KEY(parent) REFERENCES articles (id)
    # );
    # CREATE TABLE comments (
    #     entry_id INTEGER NOT NULL, 
    #     comment TEXT, 
    #     PRIMARY KEY (entry_id), 
    #     FOREIGN KEY(entry_id) REFERENCES articles (id)
    # );

    resources = parse_sql_to_frictionless_resources(sql_input)
    sys.stdout.write(json.dumps(resources, indent=2))
    package = Package(to_package_descriptor(resources))
