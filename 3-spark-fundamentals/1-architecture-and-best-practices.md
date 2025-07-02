What is Spark?
- a distributed compute framework that allows you to process large volumes of data efficiently
- it is an evolution of previous technologies, starting with Hadoop and Java MapReduce, then Hive, and now Spark

Some history
- At Facebook in the late 2010s, there was a large push to transition from Hive to Presto
- The problem with Presto is that it does everything in memory, so if you have an operation that can't fit in memory Presto just fails

What is good about Spark?
- Spark leverages RAM more effectively than previous iterations
	- ex. if you want to do a `GROUP BY` in Hive or MapReduce, everything had to be written to disk and read from disk, which was very resilient but also painfully slow.
	- Spark minimizes how much it writes to disk - it essentially only does it when it runs into an operation that it doesn't have enough memory for (Spark calls this "spilling")
		- Generally, you DON'T want Spark to spill to disk
- Spark is storage agnostic, allowing decoupling of storage and compute
	- It can read from a relational DB, a file, a key value store, etc
	- This makes it easier to avoid vendor lock-in
- There is a big Spark community!

When is Spark not good?
- When no one else in the company knows Spark
	- it's not immune to bus factor
	- maybe your company already uses something else, and it works
	- intertia is often not worth the effort to overcome

How does Spark work?
- The main components are:
	- The plan - "the play" the team runs
	- The driver - "the coach" of the team
	- The executors - "the players" of the team
- The Plan
	- These are the transformations you describe in Python/Scala/SQL
	- The plan is evaluated lazily
		- this means the plan does not run until it needs to
		- when does it "need to" run?
			- writing output, reading input
			- when part of the plan depends on the data itself
				- ex. calling `dataframe.collect()` to determine the next set of transformations
- The Driver
	- the driver reads the plan and tries to figure out "what play to make"
	- there are some important driver settings:
		- `spark.driver.memory`: the amount of memory that the driver has. for a really complex job, or when you use `dataframe.collect()` (which is mostly bad practice), you might need to bump this up
		- `spark.driver.memoryOverheadFactor`: this is the fraction the driver needs for non-heap related memory (i.e. the memory the JVM needs to run). it's usually 10%, but might need to be higher for complex jobs
	- the driver determines a few things:
		- when to actually start executing the job and stop being lazy
		- how to JOIN datasets
			- performance can rely a LOT on what *type* of JOIN spark decides to use
		- how much parallelism is needed in each step
- The Executors
	- the driver passes the plan to the executors
	- the important settings are:
		- `spark.executor.memory`: how much memory each executor gets. a low number may cause Spark to spill to disk.
			- you don't want to have too much or too little padding
		- `spark.executor.cores`: how many tasks can happen on each machine.
			- the default is 4, and you shouldn't really go higher than 6
			- if you have more than 6, you may run into a different bottleneck: the executor disk space and the throughput when tasks finish.
			- having 6 tasks on one executor also makes it more likely to OOM
		- `spark.executor.memoryOverheadFactor`: what percentage of memory each executor should use for non-heap related tasks - usually 10%.
			- you sometimes need to bump this up if you have a lot of UDFs or complexity

The Types of Joins in Spark
- Shuffle sort-merge join
	- this is typically the least performant, but it's also the most versatile and works no matter what
	- it's the default join strategy since Spark 2.3
	- works well when both sides of the join are large
	- generally speaking, you want to minimize how much this join is used
- Broadcast Hash join
	- works well if one side of the join is small
	- instead of shuffling the join, spark just ships the entire dataset to every executor so there is no shuffling 
	- setting `spark.sql.autoBroadcastJoinThreshold`: default is 10MB, and you can go as high as 8 - 10 GB, but after 1GB you may start to run into memory problems
- Bucket join
	- this is a join without shuffle

How does shuffle work?
- shuffle is the least scalable part of Spark. as scale goes up, shuffle gets more painful
- once you're over 20 - 30 TB, shuffle becomes almost impossible
- shuffle is the process of getting the data from the source files to a partition where you can do the comparison you need
- shuffle partitions and parallelism are linked
	- two settings:  `spark.sql.shuffle.partitions` and `spark.default.parallelism` are almost always the same thing
		- unless you are using the RDD API directly, which you should almost never be doing
			- this is guidance from Spark and databricks
		- so just use `spark.sql.shuffle.partitions`
			- this is the number of partitions you get after you do a join or group by

Is shuffle good or bad?
- at low - medium volume (medium volume being anything up to ~10TB)
	- it's really good and can make life a lot easier
- at high volumes > ~10TB
	- painful!
	- at high enough volumes, shuffle will completely block some pipelines
- A solution to high-volume joins can be bucketing the data
	- For example, let's say you have a high cardinality field like user_id.
		- you have to first bucket both sides of the table on user_id
		- now, when you go to join the data, you have a guarantee that ALL the data you need to do the comparison you want is already on the file, because it's pre-bucketed
		- so essentially the way you have written the files has before doing the join removes the need for the join
	- even if the two tables don't have the same number of buckets, you can still do a bucket join assuming they are multiples of one another
		- for example, 2 buckets in one table and 4 buckets in the other
		- so always bucket your table on powers of 2
	- how do you pick the number of buckets?
		- usually based on the volume of data

How do we minimize shuffle at high volumes?
- bucket the data if multiple JOINs or aggregations are happening downstream
	- if you're only doing one join though, this might be a waste
	- because remember, bucketing is not free. in order to write to a bucketed table, you need to shuffle your data upstream
- Presto can also be weird with bucketed tables
	- When you have queries on tables with a smaller number of buckets (like 8), your queries might be slow
- if you're bucketing, always use powers of 2!

Shuffle and Skew
- skew is a classic "back in my day" problem, it has gotten better
- sometimes some partitions have dramatically more data than others
- this can happen because
	- not enough partitions
	- just the natural way the data is
		- for example, imagine if the rock, beyonce and ronaldo all have a user_id that results in the same remainder when divided by 200 (default number of partitions). they will all end up on the same executor, and they have dramatically more notifications than the average facebook user

How to identify skew
- most common symptom is your job gets to 99%, takes way longer than you expect, and then fails
- another more scientific way is to do a box-and-whiskers plot of the data to see if there's extreme outliers

How to deal with skew
- adaptive query execution (only available in Spark 3+)
	- set `spark.sql.adaptive.enabled = True`
		- you don't want to set this all the time, it doesn't come for free. Spark has to compute a whole bunch of extra statistics when it runs, so it does become more expensive.
- salting the `GROUP BY` - this is the best option before Spark 3
	- this does NOT work for joins
	- you essentially add a new column that is a random number, this will break up the skew
	- first you `GROUP BY` the random number, then you aggregate + `GROUP BY` again
	- have to be careful with things like avg - should break it into SUM and COUNT and divide
```python
df.withColumn("salt_random_column", (rand * n).cast(IntegerType))
	.groupBy(groupByFields, "salt_random_column")
	.agg(aggFields)
	.groupBy(groupByFields)
	.agg(aggFields)
```
- sometimes if you need to do a join with skew before Spark 3, you can just filter out the outliers

|                           | Managed Spark (i.e. databricks) | Unmanaged (i.e. big tech) |
| ------------------------- | ------------------------------- | ------------------------- |
| should you use notebooks? | yes!                            | only for POCs             |
| how to test the job?      | run the notebook                | spark-submit from CLI     |
| version control           | git or notebook versioning      | git                       |

Notebooks
- don't really invite unit tests or integration tests
- but they invite less technical people to use spark, so that's the benefit

How to look at Spark query plans
- use `.explain()` on your dataframes
- this will show you the join strategy

How can Spark read data?
- everywhere!
- from the lake
	- delta lake, iceberg, hive metastore
- from an RDBMS
	- postgres, oracle, etc
- from an API
	- make a REST call and turn it into data
		- be careful because the rest call usually happens on the driver, so if the responses to your calls are big you could have OOM issues
		- you may want to parallelize them
			- ex get a list of URLs and do `spark.parallelize`
				- this is also a separate problem because then you put more pressure on the API
- from a flat file (csv, JSON)
- spark generally has a nicer time reading directly from the data tables than from APIs

Spark output datasets
- should almost ALWAYS be partitioned on `date`
- this should be the execution date of the pipeline
- in big tech this is called "ds partitioning"

