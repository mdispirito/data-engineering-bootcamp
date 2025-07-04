*The topics covered here are a bit of a miscellaneous grab-bag of odds and ends*

Spark Server vs.  Spark Notebooks
- Spark Server
	- you have to submit your spark job via the CLI, the session is terminated when the job completes
	- every run is fresh, things get uncached automatically
	- this can be slower, but nicer for testing
- Notebook
	- you have a persistent Spark session that you have to start and stop yourself
	- you have to be careful because if you're doing a lot of caching with your notebook, it may not mirror what will happen in production

Databricks Considerations
- In databricks, you have a live notebook that is running in production and you can... just edit it
	- This can be a bit crazy and dangerous, there's no code review or change management or version control process. To some people (including me) that is insane.
- You should always consider how you're preventing bad data from entering production

Caching and Temporary Views
- a temporary view is kind of like a CTE
- a temporary view gets recomputed every single time, unless cached
- caching
	- storage levels
		- `MEMORY_ONLY`
		- `DISK_ONLY`
			- similar in performance to a typical materialized view
			- this is basically just the same as writing out to a new table
		- `MEMORY_AND_DISK` (default)
	- caching is only great if it fits into memory
		- otherwise, you probably need a staging table in your pipeline instead
		- if you're doing a lot of disk caching, you should question it
	- in notebooks
		- call `.unpersist` when you're done otherwise the cached data will hang out
			- this is important to test your code because your notebook will run a lot faster the second time around and that won't mirror production

Caching vs. Broadcast
- Caching
	- stores pre-computed values for reuse
	- when you cache a dataset, it stays partitioned
- Broadcast Join
	- small data that gets cached and shipped in entirety to each executor
	- a couple GB is the most you want to work with
- Example
	- if you have a 100GB dataset and cache it, assuming each executor has 4 cores and there are 200 executors (so 200 partitions):
	- each executor gets 2 GB, so each task gets 500MB, and this will not overwhelm your memory
	- with a broadcast join, the entire 100GB dataset would be sent to every executor

Broadcast Join Optimization
- (one of the most important optimizations in Spark)
- broadcast JOINs prevent shuffle
	- this is GOOD!
- the threshold is set with: `spark.sql.autoBroadcastJoinThreshold`
	- the default is set at 10MB, so this is the default definition of "small"
	- but you CAN crank this up to single digit GBs, and it will still work well assuming you have enough memory
	- anything above 10GB will probably break down
- you can explicitly wrap a dataset with `broadcast(df)` as well
	- this will trigger the broadcast join regardless of the size of the dataframe
	- this can be a little easier so you don't have to worry about the small dataset slowly creeping above your threshold
	- this also makes it easier for later engineers to understand your intent

UDFs
- these allow for more complex logic and processing
- PySpark vs. Scala
	- what happens is that when the JVM is running and you hit a Python UDF, your data is serialized and passed to a separate python process which is deserialized and run, and then the returned value is serialized and sent back
		- this can make Python UDFs a lot less performant
	- Apache Arrow optimizations in recent versions of Spark have helped PySpark UDFs become more inline with ScalaSpark UDFs
		- when you're talking about "User Defined Aggregating Functions", you still take a bit of a performance hit with Python...
	- Scala Spark gives you two main advantages these days
		- UDAFs as discussed above
		- the Dataset API, which you don't get in Python
		- it doesn't come for free though - harder to learn Scala and find Scala developers
	- if you are NOT at extreme scale, you probably won't feel any performance pain with PySpark

DataFrame vs. Dataset vs. SparkSQL
- this is another big debate in Spark right now
- Dataset in Scala only
- SparkSQL is better for when you have "many cooks in the kitchen" - it's the lowest barrier to entry
	- nice when you're making rapid changes
- DataFrame is nice because you make your code more modular, making your pipelines more hardened and less likely to experience change
- Dataset API is like the furthest towards "pure software engineering" - you get everything the DataFrame gives you AND a schema
	- you can create mock data more easily
	- this good for when you require more rigorous unit and integration tests
	- it also handles NULL values better, because you have to explicitly say whether each column is nullable or not, so this makes it easier to enforce quality control
		- with the DataFrame and SparkSQL, you'll just get NULL values that show up silently

Parquet
- Iceberg uses Parquet as the default file format
- if you sort things effectively, run-length encoding allows for powerful compression
	- DON'T use global `.sort()`
		- this incurs an extra shuffle step where all the data has to be passed to one executor
		- this is slow and painful
	- use `.sortWithinPartitions()`
		- this sorts locally within the partition and you can get the benefits of run-length encoding for a low price

Spark Tuning
- Executor Memory
	- don't just set it to 16GB and call it a day, it's wasteful
	- a lot of "big tech engineers" do this because they think it's not worth their time to troubleshoot if something goes wrong
- Driver Memory
	- only needs to be bumped if you're
		- calling `df.collect`
		- have an extremely complex job
- Shuffle Partitions
	- default is 200
	- how do you pick the right number though?
		- generally speaking if your data is uniform (which it won't always be), you want  ~100 - 200MB per partition to get the right sized output datasets
			- ex. if your output dataset is 20GB, 
		- this is a good place to start but each job might be different if it's more I/O heavy or more memory heavy, etc
- AQE (adaptive query execution)
	- helps with skewed datasets, but wasteful if the dataset isn't skewed
