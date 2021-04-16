local _assertConforms(dynamic, shape) = (

  if std.isArray(dynamic) then (
    local allowedTypes = shape;
    std.foldl(
      function(result, arrayItem) (
        std.member(
          allowedTypes,
          std.type(arrayItem)
        ) && result
      ),
      dynamic,
      true
    )
  ) else if std.isObject(dynamic) then (
    std.foldl(
      function(result, key) (
        _assertConforms(dynamic[key], shape[key])
      ),
      std.objectFields(dynamic),
      true
    )
  ) else (
    std.type(dynamic) == shape
  )
);


{
  KEY_PrimaryKey: 'primaryKey',
  KEY_ForeignKey: 'foreignKey',
  KEY_Constraints: 'constraints',

  PrimaryKeyRecord: {
    id: {
      type: 'integer',
      [$.KEY_PrimaryKey]: true,
    },
  },
  defaultForeignKeyRecord(foreignTableName):: {
    // assumes the join goes over `foreignTableName`.`id`
    type: 'integer',
    [$.KEY_ForeignKey]: {
      table: foreignTableName,
      field: 'id',
    },
  },

  assertConforms(dynamic, shape):: _assertConforms(dynamic, shape),

  runTest(description, expect, result):: (
    std.trace(description, true) && std.assertEqual(expect, result)
  ),

  test_assertConforms():: [
    $.runTest('1 is a number', true, $.assertConforms(1, 'number')),
    $.runTest('a is a string', true, $.assertConforms('a', 'string')),
    $.runTest('a is not a number', false, $.assertConforms('a', 'number')),
    $.runTest('[1, 2, 3] all numbers', true, $.assertConforms([1, 2, 3], ['number'])),
    $.runTest('[1, 2, "a"] not all numbers', false, $.assertConforms([1, 2, 'a'], ['number'])),
    $.runTest('[1, 2, "a"] numbers or strings', true, $.assertConforms([1, 2, 'a'], ['number', 'string'])),
    $.runTest('object conforms', true, $.assertConforms({ x: 1 }, { x: 'number' })),
    $.runTest('object does not conform', false, $.assertConforms({ x: 1 }, { x: 'string' })),
    $.runTest('object conforms',
              true,
              $.assertConforms({
                x: 1,
                y: '2',
                z: [3, 4],
              }, {
                x: 'number',
                y: 'string',
                z: ['number'],
              })),
  ],

  propOrDefault(object, property, default=null):: (if std.objectHas(object, property) then object[property] else default),
  firstOrNull(arr):: (if std.length(arr) > 0 then arr[0] else null),
  ifElseEmptyObject(condition, valIfTrue):: (if condition then valIfTrue else {}),

  frictionlessForeignKeySpec(localField, foreignTable, foreignField):: {
    fields: localField,
    reference: {
      resource: foreignTable,
      fields: foreignField,
    },
  },
  frictionlessFieldSpec(fieldName, dataType, constraints=null):: {
    name: fieldName,
    type: dataType,
  } + (if (constraints == null || constraints == {}) then {} else { constraints: constraints }),
  jsonSchemaToFrictionlessTableResource(jsonSchema):: (
    local props = jsonSchema.properties;
    local maybePrimaryKeys = std.filter(function(k) std.objectHas(props[k], $.KEY_PrimaryKey), std.objectFields(props));
    local maybePrimaryKey = $.firstOrNull(maybePrimaryKeys);

    // NOTE: enforcing 1 primary key per table here
    $.ifElseEmptyObject(
      maybePrimaryKey != null && std.assertEqual(1, std.length(maybePrimaryKeys)),
      { primaryKey: maybePrimaryKey }
    ) + (
      local maybeForeignKeySpecs = [
        (
          local spec = props[k][$.KEY_ForeignKey];
          $.frictionlessForeignKeySpec(
            k,
            // in the frictionless articles example, the self-join specifies "" (empty string) as reference
            if $.propOrDefault(jsonSchema, 'title') == spec.table then '' else spec.table,
            spec.field,
          )
        )
        for k in std.objectFields(props)
        if std.objectHas(props[k], $.KEY_ForeignKey)
      ];
      if std.length(maybeForeignKeySpecs) > 0 then {
        foreignKeys: maybeForeignKeySpecs,
      } else {}
    ) + {
      fields: [
        $.frictionlessFieldSpec(
          k,
          props[k].type,
          $.ifElseEmptyObject(
            k == maybePrimaryKey,
            { required: true }
          ) + $.ifElseEmptyObject(
            std.objectHas(props[k], $.KEY_Constraints),
            props[k][$.KEY_Constraints]
          )
        )
        for k in std.objectFields(props)
      ],
    }
  ),
}
