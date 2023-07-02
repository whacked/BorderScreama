from typing import List, Optional
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select
from pprint import pprint
import json
import time
import random


from models.SQLModel_models import (
    TimestampedRecord,
    Device,
    VersionedSchema,
)


sqlite_file_name = ":memory:"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def main():
    # create db and tables
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        device1 = Device(name='thermometer.1', properties=json.dumps({
            'vendor': 'vendor-A',
        }))
        device2 = Device(name='thermometer=2', properties=json.dumps({
            'vendor': 'vendor B',
        }))

        session.add(device1)
        session.add(device2)

        schema1 = VersionedSchema(
            content=json.dumps({
                'title': 'SomeSchema',
                'type': 'object',
            }),
        )
        schema2 = VersionedSchema(
            content=json.dumps({
                'title': 'AnotherSchema',
                'type': 'object',
            }),
        )

        session.add(schema1)
        session.add(schema2)

        for _ in range(10):
            schema = random.choice([schema1, schema2])
            device = random.choice([device1, device2])
            tsr = TimestampedRecord(
                timestampSeconds = time.time(),
                record=json.dumps({
                    'temperature': random.random(),
                    'humidit': random.random(),
                }),
                device_id = device.id,
                versionedSchema_id = schema.id,
            )
            session.add(tsr)

        session.commit()

    with Session(engine) as session:
        statement = select(TimestampedRecord)
        results = session.exec(statement)
        for record in results:
            pprint(record)


if __name__ == "__main__":
    main()

