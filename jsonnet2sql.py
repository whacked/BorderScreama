import sys
import json
import _jsonnet as jsonnet
import os.path as _p
from jsonschema2db import JSONSchemaToPostgres


input_file_path = sys.argv[-1]
assert _p.splitext(input_file_path)[-1] in ('.jsonnet', '.json')

json_string = jsonnet.evaluate_file(input_file_path)
schema = json.loads(json_string)


class DummyConnection:
    sql_history = []

    @classmethod
    def get_statements(cls):
        return cls.sql_history

    def cursor(connection):
        class Lifecycle:
            class DummyCursor:
                def execute(self, query, args):
                    connection.sql_history.append((query, args))
            
            def __enter__(self):
                return self.DummyCursor()
            def __exit__(self, *args):
                pass

        return Lifecycle()


JSONSchemaToPostgres(
    schema,
    postgres_schema='schm',
    abbreviations={
        # source column name: target column name
        'AbbreviateThisReallyLongColumn': 'AbbTRLC'
    },
).create_tables(DummyConnection())

from pglast import prettify
for (query, args) in DummyConnection.get_statements():
    if query.startswith('create'):
        sql_pretty = prettify(query)
        sys.stdout.write(f'{sql_pretty}\n')
