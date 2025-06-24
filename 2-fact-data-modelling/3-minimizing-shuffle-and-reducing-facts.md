Why should shuffle by minimized?
- shuffle is the bottleneck for parallelism
	- if you have a pipeline that doesn't shuffle, it can be as parallel as you want it, because you don't have a specific chunk of data that you *need* to be on one machine
- some steps in big data pipelines are inherently more or less "parallelizable" than others
	- usually the more parallelism we have, the more effectively we can crunch big data (because we can use more machines)

What is shuffle?
- it's when you have to have all the data for a specific key, on the same machine

What types of queries are highly parallelizable?
- extremely parallel: `SELECT`, `FROM`, `WHERE`
	- importantly, your select does NOT use a window function
	- this query is infinitely scalable
	- imagine you have 1 million machines, each with 1 row. that's fine in this scenario, because each machine just needs to know if it fits the condition or not
- kind of parallel: `GROUP BY`, `JOIN`, `HAVING`
	- `GROUP BY`
		- going back to the previous example, let's say we have a `GROUP BY` with a key that has 30 rows in the dataset. now we need those 30 rows to be on the same machine, so they need to be moved over.
		- this is why a group by triggers a shuffle
		- in spark there is `spark.sql.shuffle.partitions` that you can configure, the default is 200
			- with this default, our million machines would pass all of their data to 200 machines
	- `JOIN`
		- join is trickier, because you have to do the whole thing twice
		- all the keys on the left and all the keys on the right need to be pushed to one machine, then the comparison needs to happen
	- `HAVING`
		- technically this is as parallel as select and where because it's a filter condition, but it goes hand-in-hand with `GROUP BY` because it needs to come after that clause.
- PAINFUL: `ORDER BY`
	- to be specific: `ORDER BY` at the end of a query, not in a window function
	- if we had a billion machines with 1 record each and we need to sort it, the ONLY way is to make sure all the data is passed through 1 machine
	- it's best to use this after you've aggregated and the number of records left is significantly lower
	- how is this different in a window function?
		- a window function does not do a global sort (assuming you use `PARTITION BY`, which you should)

Why are we talking about shuffle during fact data modelling?
- *how* the data is structured determines which keywords you have to use in your queries
- if you have data that's in a certain format, you can skip certain keywords

How do you make GROUP BY more efficient?
- give `GROUP BY` some buckets and guarantees
	- S3, Iceberg, etc supports this
	- essentially pre-shuffle the data for Spark
	- bucket the data based on a key, like UserID, usually high-cardinality integer field
	- because we have guarantees about which data is in which buckets, the `GROUP BY` can just leverage the buckets without shuffle
- reduce the data volume as much as you can!!
	- if you can reduce the data volume, your shuffles get way more efficient

How reduced fact data modelling gives you superpowers
- Fact data often has this schema
	- user_id, event_time, action, date_partition
	- very high volume, 1 row per event
- daily aggregate often has this schema
	- user_id, action_count, date_partition
	- medium sized volume, 1 row per user per day
	- can be 100x smaller, but still might be too big
- reduced fact --> take this one step further
	- user_id, action_count[], month_start_partition / year_start_partition
		- you can either have 1 row / month or 1 row / year per user
	- lowest volume
	- this can minimize the amount of shuffling
	- keep in mind this is NOT a monthly or yearly aggregate
	- this basically stores the date as an index or an offset in an array, instead of storing it as a string in each row
- there are tradeoffs
	- as the data gets smaller, you lose some flexibility around what type of analytics you can do with it
	- the full fact data schema is very flexible, you can answer whatever you want, but it's VERY hard to use at longer time horizons
	- with daily aggregate tables, you can do longer time horizons - they usually work well for 1 or 2 years
		- this schema is sometimes called a "metric repository"

fPotential impacts of reduced fact modelling
- multi-year analyses can take hours instead of weeks
- "decades-long slow burn" analyses can be unlocked