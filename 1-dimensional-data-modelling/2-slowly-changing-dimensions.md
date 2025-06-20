Slowly changing dimensions
- an attribute than drifts over time
- slowly changing dimensions have a "time frame"
- if you don't model them the right way, they impact idempotency
	- ability for the pipelines to produce the same result when run over and over again

Idempotent Pipelines
- it has to produce the same result regardless of when it's run
	- regardless of the day you run it, the hour you run it, or how many times you run it

What makes pipelines not idempotent?
- `INSERT INTO` without `TRUNCATE`
	- the second time you've run it, there's duplicated data
	- use `MERGE` or `INSERT OVERWRITE` every time to avoid this
	- Generally you can avoid `INSERT INTO`
- Using `start_date >` without a corresponding `end_date <`
	- this means each day that passes, you get an additional day of data
	- so this gets a different result depending on when it's run
	- this can also create OOM exceptions when you backfill
- Not using a full set of partition sensors
	- pipeline might run with an incomplete set of inputs
		- for example, before all the input data is ready
- Not using `depends_on_past` (airflow term) for cumulative pipelines
	- also called `sequential processing`
- Relying on the "latest" partition of a not properly modelled SCD table

The pains of not having idempotency
- Backfilling causes inconsistencies between old and restated data
- Unit tests can't replicate the production behaviour
- Silent failures - the pipelines will still run, they'll just have bad data quality

Should you model as slowly changing dimensions?
- The creator of Airflow hates SCD modelling...
	- His opinion is that, as an example, there should be a record every day with your age, even though the value will be duplicated, because storage is cheap, and idempotency issues are expensive
- Options for modelling
	- Latest snapshot --> only hold on to the latest value
		- problem with this is the pipeline is inherently non-idempotent
	- Daily/monthly/yearly snapshot
	- SCD
		- essentially collapsing daily snapshots based on whether the data changed
			- For example, 1 row that says i'm 18 years old from date x to date y, instead of 365 rows
- Should you model it as a SCD?
	- Depends how slowly it changes. If it's not that slowly (ex changes every week), you don't save a lot by modelling it that way.

Why do dimensions change?
- people's preferences change
- people move to new countries...
- all types of reasons

How do we model dimensions that change?
- Singular snapshots (backfill will only the latest snapshot)
	- These are not idempotent, so almost never do this
- Daily partitioned snapshots
- SCD Types 1, 2, 3
	- Type 0 --> actually not changing
		- Ex. birth date
	- Type 1 --> the value changes but you only care about the latest value
		- Maybe this is okay for online apps? But not analytics
	- Type 2 --> you care about what the value was from `start_date` to `end_date`
		- These are purely idempotent
		- Current values will have the `end_date` either `NULL` or far into the future like `9999-12-31`
		- Could also have another boolean column `is_current`
		- Harder to use, since there's more than 1 row per dimension
	- Type 3 --> you only care about the original and current values
		- Benefits: only 1 row per dimensions
		- Drawback: you lose history between original and current
		- Is it idempotent? Partially, which means no

SCD2 Loading
- Load the entire history in one query
	- Inefficient but nimble, only 1 query needed
- Incrementally load the data after the previous SCD is generated
	- Has the `depends_on_past` constraint
	- Efficient but cumbersome