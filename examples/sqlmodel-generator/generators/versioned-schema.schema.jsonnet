{
  title: 'VersionedSchema',
  type: 'object',
  properties: {
    id: {
      type: 'integer',
      primary_key: true,
    },
    parents: {
      // too hard to handle by autogen now
      // type: 'array',
      // items: {
      //   '$ref': '#',  // self reference
      // },
    },
    transformerCode: {
      type: 'string',
    },
    content: {
      type: 'string',
    },
    sha256: {
      type: 'string',
    },
  },
  required: ['content'],
}
