import logging
import jsonschema
import os
import os.path as _p
import json
import yaml
import importlib
import sys
from textwrap import indent
from pydantic.schema import field_class_to_schema


logger = logging.getLogger(__name__)


_primitives = { str, dict, list, tuple, int }
_jsonschema_type_to_python = {
    jsonschema_type['type']: python_class
    for python_class, jsonschema_type
    in field_class_to_schema
    if python_class in _primitives
}


def get_python_type_name(jsonschema_item_typedef):
    return _jsonschema_type_to_python[
        jsonschema_item_typedef["type"]
    ].__name__

def generate_pydantic_model_skeleton(model_name: str, jss: dict):
    instance_fields_skeleton = '\n'.join([
        f'{field_name}: {get_python_type_name(field_props)}'
        for field_name, field_props
        in jss['properties'].items()
    ])
    return f'''\
from pydantic import BaseModel


class {model_name}(BaseModel):
{indent(instance_fields_skeleton, '    ')}
'''


class SchemaLoader(object):

    _registered_schemas = {}

    _file_parsers = {
        '.json': json.loads,
        '.yaml': yaml.safe_load,
        '.yml': yaml.safe_load,
    }

    @classmethod
    def load_from_directory(cls, directory):
        start_directory = _p.abspath(directory)
        loaded = []
        for basedir, subdirs, files in os.walk(start_directory):
            reldir = _p.relpath(basedir, start_directory)
            if reldir.startswith('.'):
                continue
            for file in files:
                relpath = _p.join(reldir, file)
                namespace, ext = _p.splitext(relpath)
                if ext not in cls._file_parsers:
                    continue
                logger.debug(f'parsing handled extension {ext} for {relpath}')
                parser = cls._file_parsers[ext]
                parsed = parser(open(_p.join(start_directory, relpath)).read())
                if cls.register(namespace, parsed):
                    loaded.append(namespace)
        return loaded

    @classmethod
    def write_to_directory(cls, directory):
        start_directory = _p.abspath(directory)
        for namespace, schema in cls._registered_schemas.items():
            json_path = _p.join(start_directory, f'{namespace}.json')
            if _p.exists(json_path):
                logger.warning(f'overwriting {json_path}')
            else:
                logger.info(f'writing {json_path}')
            with open(json_path, 'w') as ofile:
                ofile.write(json.dumps(schema, indent=2))

    @classmethod
    def sync_with_directory(cls, directory):
        if directory not in sys.path:
            sys.path.append(directory)
        loaded = cls.load_from_directory(directory)
        for namespace in loaded:
            module_path = namespace.replace(os.sep, '.')
            module_base, module_class = _p.split(namespace)
            module_base_dir = _p.join(
                    directory,
                    module_base)
            init_py_path = _p.join(module_base_dir, '__init__.py')
            module_py_path = _p.join(module_base_dir, f'{module_class}.py')
            if not _p.exists(init_py_path):
                with open(init_py_path, 'w') as ofile:
                    ofile.write('')
            if _p.exists(module_py_path):
                logger.info(f'python module found for {namespace} at {module_py_path}')
            else:
                logger.warning(f'python module missing for {namespace} at {module_py_path}; generating...')
                schema_jsonschema_definition = cls._registered_schemas[namespace]
                generated_python = generate_pydantic_model_skeleton(module_class, schema_jsonschema_definition)
                with open(module_py_path, 'w') as ofile:
                    ofile.write(generated_python)

            module = importlib.import_module(f'{module_path}')
            imported_class = getattr(module, module_class)
            jss = cls._registered_schemas[namespace]
            if jss != imported_class.schema():
                logger.error('python class different from jsonschema')
                print('=== JSONSCHEMA ===')
                print(jss)
                print('=== PYTHON CLASS ===')
                print(imported_class.schema())

    @classmethod
    def register(cls, namespace, definition):
        if namespace in cls._registered_schemas:
            existing_definition = cls._registered_schemas[namespace]
            if existing_definition != definition:
                raise Exception(f'trying to re-register schema with non-matching-definition for {namespace}')
            else:
                logger.warning(f'skipping duplicate schema registration attempt for {namespace}')
        logger.info(f'registering schema for {namespace}')
        cls._registered_schemas[namespace] = definition
        return True

