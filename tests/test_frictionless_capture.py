import json
from frictionless import Package
from BorderScreama.frictionless_capture import (
    get_generated_sql,
    load_schema,
    to_package_descriptor,
)
from tableschema import Schema


articles = Schema('https://raw.githubusercontent.com/frictionlessdata/datapackage-pipelines-sql-driver/master/data/articles.json')
package = Package(to_package_descriptor(
    [{'name': 'articles', 'schema': articles.descriptor},
     'https://raw.githubusercontent.com/frictionlessdata/datapackage-pipelines-sql-driver/master/data/comments.json']))

assert get_generated_sql(package).strip() == '''\
CREATE TABLE articles (
	id INTEGER NOT NULL, 
	parent INTEGER, 
	name TEXT, 
	current BOOLEAN, 
	rating NUMERIC, 
	created_year DATE, 
	created_date DATE, 
	created_time TIME, 
	created_datetime DATETIME, 
	stats JSONB, 
	persons JSONB, 
	location JSONB, 
	PRIMARY KEY (id), 
	FOREIGN KEY(parent) REFERENCES articles (id)
)


CREATE TABLE comments (
	entry_id INTEGER NOT NULL, 
	comment TEXT, 
	PRIMARY KEY (entry_id), 
	FOREIGN KEY(entry_id) REFERENCES articles (id)
)
'''.strip()
