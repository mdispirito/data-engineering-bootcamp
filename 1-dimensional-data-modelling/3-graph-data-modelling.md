What makes a dimension additive?
- additive means you don't "double count"
- for example, population is additive
- number of honda drivers is NOT additive
	- does NOT equal civic drivers + corolla drivers + accord drivers... because a driver can own a corolla and an accord
- key question to ask to determine if a dimensions is additive is "can a user be two of them at the same time?"
	- ex. can a user be an iphone and an android user at the same time? yes,  so it's not additive

How does additivity help?
- you don't need to use `COUNT(DISTINCT)` on pre-aggregated dimensions
- non-additive dimensions are usually only non-additive with `COUNT`, but not `SUM`
	- for example, miles driven by honda drivers = miles driven by corolla drivers + miles driven by accord drivers... etc

When should you use enums?
- enums are great for low - medium cardinality
- Country is a great example of where enums start to struggle
- a rule of thumb is less than 50 values makes them work well

Why should you use enums?
- built in data quality for free
	- if you model a field as a enum and then you get an invalid value, the pipeline will fail
- built in static fields
- built in documentation
	- you know what all the possible values of a field can be, vs. not knowing if it's a string

Enumerations and subpartitions
- enums make amazing subpartitions
	- because you have an exhaustive list of possible values
	- they chunk up the big data problem into manageable pieces

Example enum pattern [here](https://github.com/EcZachly/little-book-of-pipelines)
- Use case is whenever you have tons of sources mapping to a shared schema

How do you model data from disparate sources into a shared schema?
- you don't want to bring in all columns from all tables...
- you want a flexible schema

Flexible Schema
- Benefits
	- you don't have to run `ALTER TABLE`, you can just add another key to the map
	- you can manage more columns
	- your schemas don't have a ton of `NULL` columns
	- `other_properties` column is is nice for rarely-used-but-needed-columns
- Drawbacks
	- Compression is usually worse, especially if you use JSON
		- Main reason is that in a table the column header is stored once, but in a map it's stored in each record
	- Readability, queryability

How is graph data modelling different?
- it's relationship focused, not entity focused
- almost all graph databases have the same schema... the model for each vertex usually looks like
	- `Identifier: STRING`
	- `Type: STRING`
	- `Properties: MAP<STRING, STRING>`
- Graph data modelling shifts the focus from how things *are* to how things *are connected*
- the model for each edge (or connection) usually looks like
	- `subject_identifier: STRING`
	- `subject_type: VERTEX_TYPE`
	- `object_identifier: STRING`
	- `object_type: VERTEX_TYPE`
	- `edge_type: EDGE_TYPE`
	- `properties: MAP<STRING, STRING>`
- example with sports: subject is a player, object is a team, edge is `plays_on`, properties include `years they played on the team`, etc...
