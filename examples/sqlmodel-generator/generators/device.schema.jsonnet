{
  title: 'Device',
  type: 'object',
  properties: {
    id: {
      type: 'integer',
    },
    name: {
      type: 'string',
    },
    properties: {},
    tags: {
      type: 'array',
      items: {
        '$ref': './tag.schema.json',
      },
    },
  },
  required: ['name'],
}
