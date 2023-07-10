define generate_json
	# note we strip $ref to prevent it leading to circular references
	jsonnet $< | jq -S | tee $@
	check-jsonschema --check-metaschema $@
endef

define generate_model
	python -m datamodel_code_generator \
		--input $< \
		--output $@ \
		--class-name $(basename $(notdir $@)) \
		--field-extra-keys primaryKey \
		--input-file-type jsonschema \
		--disable-timestamp
endef

define generate_sqlmodel
	cat $< | \
		sed 's|class |class Sql|' | \
		sed 's|from pydantic import BaseModel|from sqlmodel import SQLModel as BaseModel|' | \
		tee $@
endef

schemas/%.schema.json: generators/%.schema.jsonnet
	$(call generate_json,$<,$@)

schemas: \
	schemas/timestamped-record.schema.json \
	schemas/device.schema.json \
	schemas/tag.schema.json \
	schemas/versioned-schema.schema.json

models/TimestampedRecord.py: schemas/timestamped-record.schema.json
	python ../BorderScreama/pydantic_codegen.py --schema-path $< | \
		tee $@

models/Device.py: schemas/device.schema.json
	$(call generate_model,$<,$@)

models/Tag.py: schemas/tag.schema.json
	$(call generate_model,$<,$@)

models/VersionedSchema.py: schemas/versioned-schema.schema.json
	$(call generate_model,$<,$@)

models: \
	models/SQLModel_models.py

models/SQLModel_models.py: schemas/timestamped-record.schema.json schemas/device.schema.json schemas/versioned-schema.schema.json schemas/tag.schema.json
	python ../../BorderScreama/sqlmodel_codegen.py --schema-paths $^ | \
		tee $@

