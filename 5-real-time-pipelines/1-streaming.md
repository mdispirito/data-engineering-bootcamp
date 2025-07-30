What is a streaming pipeline?
- streaming pipelines process data in a low-latency way

Streaming vs. Near Real-Time vs. Real-Time
- streaming (or continuous processing)
	- when an event is generated, it is processed immediately
	- ex: Flink
- near real-time
	- data is processed in small batches every few minutes
		- i.e. micro-batches
	- ex: Spark Structured Streaming
- real-time and streaming are often synonymous, but not always
	- ensure you understand latency requirements

What does real-time mean from stakeholders?
- it rarely means streaming
- it usually just means low-latency or predictable refresh rate
- most often, a daily pipeline meets requirements

Should you use streaming?
-  Considerations include:
	- skills on the team
	- what is the incremental benefit?
	- homogeneity of your pipelines
	- what is the tradeoff between daily batch, hourly batch, microbatch and streaming?
	- how is data quality going to be done?
		- obviously, batch pipelines have a much easier DQ path

Streaming-only use cases
- detecting fraud, preventing bad behaviour
	- if someone steals your credit card, you'd like it if they couldn't go on a 24hr spending spree before the fraud detection pipeline runs
- high-frequency trading
- live event processing
	- ex. live sports analytics

Grey-area use cases
- data that is served to customers
	- ex. if you have a master dataset with many downstream dataset dependencies, then streaming can allow all your consumers to fire sooner
	- this also may let you spread your compute out over the day rather than have all your consumers firing at the same time

No-go streaming use cases
- analysts complaining that data isn't up-to-date, i.e. a day behind
	- if it was up to date, what would the impact to the business be?
	- the velocity of most business decisions is not < 1 day

How are streaming and batch pipelines different?
- streaming pipelines are running 24/7
	- so the probability that it breaks is simply higher
- streaming pipelines are more software engineering-oriented
	- they act more like web servers than DAGs
- you really need unit and integration tests for your streaming jobs

The Streaming -> Batch Continuum
- real-time is a myth
	- you'll still have seconds of latency from event generation with kafka -> flink -> sink
- pipelines can be broken into 4 categories
	- daily batch
	- hourly batch (sometimes called near real-time)
	- microbatch (sometimes called near real-time)
	- continuous processing (usually called real-time)

Structure of a streaming pipeline
- The sources
	- Kafka is the poster-child
		- the main competitor is RabbitMQ, which does not scale quite as well but has some more complex message routing mechanisms
	- Enriched dimensional sources (i.e. side inputs)
- The compute engine
	- Flink
	- Spark Structured Streaming
- The destination, i.e. "the sink"
	- common sinks
		- another kafka topic
		- data lake - iceberg
		- postgres

Sidenote on Iceberg
- one reason it was created was to solve for the streaming use case
- before you had the Hive metastore, and to add to it you needed to overwrite the old partitions
	- you could not add new data to a partition that already existed
	- this is because Hive was very batch-oriented
- Iceberg lets you append new data to existing partitions
- Iceberg is streaming-friendly, but the tables can also be easily queried by batch pipelines as well

Streaming Challenges
- out of order events, and how you properly manage them
- late arriving data
	- in the batch world, this doesn't have such a big impact 
- recovering from failures
	- the longer you wait to fix a streaming pipeline, the more it gets "backed up"

Out of order events
- how does Flink deal with them?
	- you specify a "watermark" in your event stream
	- this basically works by giving yourself a window (or a buffer), such as 15 seconds, where the events could be out of order, and Flink fixes them for you

Recovering from failures
- Flink manages this in a few ways. When flink starts up, you have to tell it to start from one of:
	- Checkpoints - the primary way
		- you can tell Flink to checkpoint event n seconds, and it saves the state of the job at that time
	- Offsets
		- earliest offset (read in everything that's in kafka, as far back as possible)
		- latest offset (only read in new data after the job stops)
		- specific timestamp (only read data at the timestamp or newer)
	- Savepoints
		- checkpoints are internal to Flink, but savepoints are more system-agnostic

Late arriving data
- how late is too late? you have to choose