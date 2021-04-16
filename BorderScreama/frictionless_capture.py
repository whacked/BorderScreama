import os.path as _p
import json
import sqlalchemy.dialects.postgresql
from sqlalchemy import util
from sqlalchemy.engine import url as _url
from sqlalchemy.engine.mock import MockConnection
from unittest.mock import patch
from tableschema import Schema
from frictionless import Package


def load_schema(json_path):
    '''
    convenience function to load using Schema()
    but bailing if it doesn't look like a schema
    '''
    schema = Schema(json_path)
    assert len(schema.fields) > 0
    return schema


def to_package_descriptor(schema_json_files_or_data):
    out = {'resources': []}
    for maybe_file_path in schema_json_files_or_data:
        if isinstance(maybe_file_path, str):
            schema = load_schema(maybe_file_path)
            resource = {
                'name': _p.splitext(_p.split(maybe_file_path)[1])[0],
                'path': maybe_file_path,
                'schema': schema.descriptor,
            }
        else:
            resource = maybe_file_path
            assert isinstance(resource, dict)
            assert resource['name'] is not None
        out['resources'].append(resource)
    return out


class MyMockConnection(MockConnection):
    # ref sqlalchemy.create_mock_engine

    POSTGRESQL_DSN = 'postgresql://fake'
    SQLITE_DSN = 'sqlite://fake'

    _history = []

    def close(*args):
        return args

    def begin(*args):
        class Lifecycle:
            class DummyCursor:
                pass
            def __enter__(self):
                return self.DummyCursor()
            def __exit__(self, *args):
                return args

        return Lifecycle()
    
    def __enter__(*args):
        pass
    
    def __exit__(*args):
        pass
    
    def _execute_clauseelement(*args):
        print(f'<executing> {args}')

    @classmethod
    def render_history(cls):
        return ''.join(cls._history)

    @classmethod
    def create_mock_engine(cls, dsn=POSTGRESQL_DSN, **kw):
        '''
        dsn: str, e.g.:
        - postgresql://fake
        - sqlite://fake
        '''
        # create url.URL object
        u = _url.make_url(dsn)
        dialect_cls = u.get_dialect()
        dialect_args = {}
        # consume dialect arguments from kwargs
        for k in util.get_cls_kwargs(dialect_cls):
            if k in kw:
                dialect_args[k] = kw.pop(k)

        # create dialect
        dialect = dialect_cls(**dialect_args)
        
        def dump(sql, *multiparams, **params):
            # this piece is effected when run directly in the same file;
            # unclear reason now, don't really care
            # query = sql.compile(dialect=cls.dialect)
            cls._history.append(str(sql))
        
        return cls(dialect, dump)


def run_sql_in_mock_engine(package, mock_engine_dsn=MyMockConnection.POSTGRESQL_DSN):
    # NOTE: not set up to support sqlite3 directly
    #       it's simpler to actually create the db
    #       then .schema the result

    # use real engines
    # from sqlalchemy import create_engine
    # engine = create_engine('sqlite:///test.db')
    # engine = create_engine('postgresql://localhost:5432/testdb')
    # package.to_sql(engine)
    engine = MyMockConnection.create_mock_engine(mock_engine_dsn)

    with patch.object(
        sqlalchemy.dialects.postgresql.base.PGDialect, 'get_table_names'
    ) as mocked_execute1, patch.object(
        sqlalchemy.dialects.postgresql.base.PGDialect, 'get_view_names'
    ) as mocked_execute2:

        # we dont care what the return value of the dependency is
        mocked_execute1.return_value = []
        mocked_execute2.return_value = []
        package.to_sql(engine)
        return engine

def get_generated_sql_statements(package):
    return run_sql_in_mock_engine(package)._history

def get_generated_sql(package):
    return run_sql_in_mock_engine(package).render_history()
