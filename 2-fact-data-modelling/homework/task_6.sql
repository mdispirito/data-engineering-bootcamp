-- The incremental query to generate `host_activity_datelist`

/*
This query is just for learning/lab purposes.
In a production setting, we'd pass the dates as params to do a daily incremental load.
*/
INSERT INTO hosts_cumulated
WITH yesterday AS (
	SELECT *
	FROM hosts_cumulated
	WHERE date = DATE('2022-12-31')
), today AS (
	SELECT
		host,
		DATE(CAST(event_time AS TIMESTAMP)) AS date_active
	FROM events
	WHERE DATE(CAST(event_time AS TIMESTAMP)) = DATE('2023-01-01')
	AND host IS NOT NULL
	GROUP BY host, DATE(CAST(event_time AS TIMESTAMP))
)
SELECT
	COALESCE(t.host, y.host) AS host,
	CASE
		WHEN y.dates_active IS NULL
			THEN ARRAY[t.date_active]
		WHEN t.date_active IS NULL
			THEN y.dates_active
		ELSE ARRAY[t.date_active] || y.dates_active
	END AS dates_active,
	COALESCE(t.date_active, y.date + INTERVAL '1 day') AS date
FROM today t
FULL OUTER JOIN yesterday y
ON t.host = y.host