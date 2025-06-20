Complex data types: array, struct
- are important for being able to compact datasets
- the tradeoff is they are harder to work with and query

Dimensions
- attributes of an entity (user's birthday, user's favourite food)
- some dimensions may identify an entity (ID, SSN, device ID)
- some dimensions are just attributes
- attributes come in two flavours
	- fixed
		- a birthday, phone manufacturer
	- slowly changing (time dependent)
		- favourite food

Knowing your Data Consumer
- Data Analysts/Scientists
	- maybe prefer data that is easy to query
- Data Engineers
	- this is the case where more complexity is okay for compactness/performance
	- you may run into "master" data, which is data that other DEs depend on in other pipelines
- ML Models
	- they want ID, and then usually flattened decimal columns
	- but depends on the model...
	- maybe you don't need to care as much about naming
- Customers
	- should be easy to interpret
	- charts are best

OLTP vs. OLAP vs. master data
- OLTP
	- mostly outside the DE world. used by SWEs to optimize for low latency (low volume queries)
	- 3rd normal form, minimizing data duplication
	- need a lot of joins to get data you want
- OLAP
	- mostly used for large-volume, GROUP BY queries, minimize joins
	- modelling the data correctly should avoid huge joins
- Master Data ("middle ground")
	- you still want entities deduped
	- optimizes for completeness of entity definition

Mismatched needs
- a transactional system modelled as analytical will be slow
	- it will pull it data it doesn't need in extra columns
- an analytical system modelled as transactional will have painful joins, leading to shuffles and cost

Data Continuum
- Production DB snapshots --> Master Data --> OLAP Cubes --> Metrics
- Often times going from prod DB to master data joins 10s of transactional tables together
- OLAP cubes are flattened, may have multiple rows per entity, good for grouping by user, product, etc
- Metrics are a big aggregation
	- Ex: Average listing place across all of AirBNB

Cumulative Table Design
- All about holding on to history (ex. view of a customer yesterday and today)
- Core components
	- 2 data frames/tables (yesterday and today)
	- FULL OUTER JOIN them together
		- there might be data in yesterday that isn't in today, and vice versa
	- COALESCE the values to keep everything around
	- this keeps all history around
	- The cumulative output of today becomes tomorrow's input
- Usage
	- State Transition Tracking
		- ex. users churned, resurrected, new
- This pattern is common for creating master data
- Strengths
	- Historical analysis without shuffling/group by
		- Ex. when user was last active
		- For example you can have the last 30 days of data in one row with an array
		- Then you need to select 1 row instead of 30 and then doing joins
	- Transition analysis is easy
- Drawbacks
	- Backfills can only be handled sequentially, because each day relies on the previous day
		- This is painful!
	- Daily data can be backfilled in parallel
	- PII can be messy since inactive users get carried forward

Compactness vs. Usability Tradeoff
- The most usable tables usually have an ID and no complex data types
	- Can easily be manipulated with WHERE and GROUP BY
	- Useful for the "OLAP cube" layer
- The most compact tables are usually not human readable, and are just an ID and a blob of bytes
	- Usually need to decompress the data and decode it before querying
	- But this helps with network I/O
	- All about online systems!
- Middle-ground tables
	- Use complex tables (array, map, struct), making queries trickier but a bit more compact
	- Useful for the "master data layer"

Data Types
- Struct
	- Keys are rigidly defined, compression is good
	- values can be any type
- Map
	- Keys are loosely defined, compression is okay
	- Values all have to be the same type
- Array
	- Ordinal
	- List of values that all have to be the same type
