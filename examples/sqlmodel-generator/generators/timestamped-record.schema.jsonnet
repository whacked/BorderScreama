{
  title: 'TimestampedRecord',
  type: 'object',
  properties: {
    id: {
      type: 'integer',
    },
    timestampSeconds: { type: 'number' },
    versionedSchema: {
      '$ref': './versioned-schema.schema.json',
    },
    device: {
      '$ref': './device.schema.json',
    },
    record: {},
  },
  required: ['timestampSeconds', 'schema', 'record'],
}
