local util = import '../../templates/util.jsonnet';
local Base = import '_Base.jsonnet';


util.jsonSchemaToFrictionlessTableResource(Base {
  title: 'articles',
  properties: {
    id: {
      type: 'number',
      description: 'id',
      [util.KEY_PrimaryKey]: true,
    },
    parent: {
      type: 'number',
      [util.KEY_ForeignKey]: {
        table: 'articles',
        field: 'id',
      },
    },
    current: {
      type: 'boolean',
    },
    rating: {
      type: 'number',
    },
    created_year: {
      type: 'date',
      format: '%Y',
    },
    created_date: {
      type: 'date',
    },
    created_time: {
      type: 'time',
    },
    created_datetime: {
      type: 'datetime',
    },
    stats: {
      type: 'object',
    },
    persons: {
      type: 'array',
    },
    location: {
      type: 'geojson',
    },
  },
})
