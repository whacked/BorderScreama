import jsonschema
from pydantic import BaseModel, Field, PositiveInt
from BorderScreama import *
from pprint import pprint
import logging
import coloredlogs


logging.basicConfig()
logger.setLevel(logging.DEBUG)
coloredlogs.install(level=logging.DEBUG)


class Model(BaseModel):
    foo: PositiveInt = Field(..., exclusiveMaximum=10)


class JwtSessionContext(BaseModel):
    message: str
    username: str
    url: str
    jwt_payload: str


SchemaLoader.register('tester', Model)
SchemaLoader.register('tester', Model)
# SchemaLoader.load_from_directory('.')

loader = SchemaLoader()
# pprint(Model.schema())
pprint(JwtSessionContext.schema())

