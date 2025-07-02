/*
- An incremental query that loads `host_activity_reduced`
  - day-by-day
*/

INSERT INTO host_activity_reduced
WITH daily_aggregate AS (
	SELECT
		host,
		DATE(event_time) as date,
		COUNT(1) AS hits,
		COUNT(DISTINCT user_id) AS unique_visitors
	FROM events
	WHERE DATE(event_time) = DATE('2023-01-03')
	AND host IS NOT NULL
	AND user_id IS NOT NULL
	GROUP BY host, DATE(event_time)
), yesterday_array AS (
	SELECT *
	FROM host_activity_reduced
	WHERE month_start = DATE('2023-01-01')
)
SELECT
	COALESCE(da.host, ya.host) AS host,
	-- since da.date moves forward every day, we need to use
	-- DATE_TRUNC to keep it set as the starting day of the month
	COALESCE(ya.month_start, DATE_TRUNC('month', da.date)) AS month_start,
	-- as opposed to previous exercises where the most recent value is at the 0th index in the array,
	-- in this case we want to append the newest values to the end of the metrics array
	CASE
		WHEN ya.hit_array IS NOT NULL
			THEN ya.hit_array || ARRAY[COALESCE(da.hits, 0)]
		WHEN ya.hit_array IS NULL
			-- we're unlikely to need this case, 
			-- but just in case some hosts don't get hits until later in the month,
			-- we should account for it
			THEN ARRAY_FILL(0, ARRAY[COALESCE(date - DATE(DATE_TRUNC('month',  date)), 0)]) || ARRAY[COALESCE(da.hits, 0)]
	END AS hit_array,
	CASE
		WHEN ya.unique_visitors_array IS NOT NULL
			THEN ya.unique_visitors_array || ARRAY[COALESCE(da.unique_visitors, 0)]
		WHEN ya.unique_visitors_array IS NULL
			-- same as above, we're unlikely to need this case, but it's here for safety
			THEN ARRAY_FILL(0, ARRAY[COALESCE(date - DATE(DATE_TRUNC('month',  date)), 0)]) || ARRAY[COALESCE(da.unique_visitors, 0)]
	END AS unique_visitors_array
FROM daily_aggregate da
FULL OUTER JOIN yesterday_array ya
ON da.host = ya.host
-- we need to handle overwrites with the below,
-- since postgres won't do that automatically
ON CONFLICT (host, month_start)
DO UPDATE SET 
		hit_array = EXCLUDED.hit_array,
		unique_visitors_array = EXCLUDED.unique_visitors_array