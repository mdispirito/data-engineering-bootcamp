Care about the number of table scans
- `COUNT(CASE WHEN)` is a powerful way to put conditions in your aggregation statement and only scan the table once
- cumulative table design minimizes table scans

Clean SQL code
- common table expressions are your friend
- use aliases, don't leave derived columns unnamed

Advanced SQL Techniques to try
- `GROUPING SETS` / `GROUP BY CUBE` / `GROUP BY ROLLUP`
	- a way to do multiple aggregations in one query without nasty unions
- self-joins
- window functions
- `CROSS JOIN UNNEST / `LATERAL VIEW EXPLODE`
	- unnest can turn an array back into rows
	- these two basically do the same thing

Grouping Sets
```sql
FROM events_augmented
GROUP BY GROUPING SETS (
	(os_type, device_type, browser_type),
	(os_type, browser_type),
	(os_type),
	(browser_type)
)
```
- without grouping sets, you need 4 separate queries with different group bys
	- and then if you want to union the queries, you need to add some dummy values
- this also has performance benefits over UNION ALL
- also more readable and maintainable
- one thing to watch out for is to make sure the columns you are including are not nullable
	- this is because in the grouping sets where some columns are ignored, the SQL engine will nullify those columns

Cube
```sql
FROM events_augmented
GROUP BY CUBE(os_type, device_type, browser_type)
```
- this gives you all possible permutations
	- ex. all three, every combination of two, and then every combination of one, then the overall aggregate
- obviously, the number of permutations explodes as the number of dimensions goes up (n dimensions = n factorial permutations) - you probably don't want to use more than three
- downside here is that you don't always care about every single combination
- this is generally just worse than grouping sets or rollup - you are giving up a lot of control for no reason.
	- the one use case for this might be some fast, ad-hoc exploratory data analysis on a relatively small dataset

Rollup
```sql
FROM events_augmented
GROUP BY ROLLUP(os_type, device_type, browser_type)
```
- we usually use this for hierarchical data
	- for example, grouping on country, then country+state, then country+state+city

Window Functions
- the function (usually, RANK, SUM, AVG, DENSE_RANK, LAG, LEAD)
	- RANK, DENSE_RANK and ROW_NUMBER basically do the same thing - they give an ordinal output based on another column
		- usually you don't want RANK over DENSE_RANK or ROW_NUMBER
			- one exception is if you're analyzing the olympics, there's a tie for 2nd, and there's no 3rd place, the next place is 4th. lol
- the window
	- `PARTITION BY` - how you cut up your window
	- `ORDER BY` - how you sort the window, you need it for ranking or rolling sums
	- `ROWS` - determines how big the window can be

Data Modeling vs. Advanced SQL
- if your data analytics need to do SQL gymnastics to solve their analytics problems, there is a data engineering problem
	- when starting a job, you should always understand where the analytics partners are at and what their bottlenecks are

Symptoms of Bad Data Modeling
- slow dashboards
	- you need to pre-aggregate your data
	- grouping sets can be useful here
	- you don't want daily-level data that is not pre-aggregated to feed your dashboard
- queries with a weird number of CTEs
	- if there are a lot, like 10... usually the first few need to be separated into a staging table (that potentially has a short retention period if needed)
		- even outside of maintainability, storage is always cheaper than compute
- lots of `CASE WHEN` statements in the analytics queries
	- usually means you're not conforming the values in your model to what they need to be
