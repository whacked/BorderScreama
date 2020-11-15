import logging
import jsonschema
import os
import os.path as _p
import json
import yaml


logger = logging.getLogger(__name__)


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
                parsed = parser(open(relpath).read())
                cls.register(namespace, parsed)

    @classmethod
    def register(cls, namespace, definition):
        if namespace in cls._registered_schemas:
            existing_definition = cls._registered_schemas[namespace]
            if existing_definition != definition:
                raise Exception(f'trying to re-register schema with non-matching-definition for {namespace}')
            else:
                logger.warning(f'skipping duplicate schema registration attempt for {namespace}')
                return
        logger.info(f'registering schema for {namespace}')
        cls._registered_schemas[namespace] = definition

