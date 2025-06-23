-- Task 4: Write a "backfill" query that can populate the entire actors_history_scd table in a single query
-- Running the below query with `INSERT INTO` can load actors_history_scd table defined in task_3.
-- The downside of this query is it scans all of history, which not might be performant enough depending on the scale.
WITH with_previous AS (
	SELECT
		actor,
		actorid,
		current_year,
		quality_class,
		is_active,
		LAG(quality_class, 1)
			OVER (PARTITION BY actorid ORDER BY current_year) AS previous_quality_class,
		LAG(is_active, 1) 
			OVER (PARTITION BY actorid ORDER BY current_year) AS previous_is_active
	FROM actors
	-- current_year would be injected as a param in a real world pipeline
	WHERE current_year <= 2021
),
with_indicators AS (
	SELECT *,
		CASE
			WHEN quality_class <> previous_quality_class THEN 1
			WHEN is_active <> previous_is_active THEN 1
			ELSE 0
		END AS change_indicator
	FROM with_previous
),
with_streaks AS (
	SELECT *,
		SUM(change_indicator) OVER (PARTITION BY actorid ORDER BY current_year) AS streak_identifier
	FROM with_indicators
)
SELECT
	actorid,	
	actor,
	quality_class,
	is_active,
	MIN(current_year) as start_date,
	MAX(current_year) as end_date,
	-- current_year would be injected as a param in a real world pipeline
	2021 AS current_year
FROM with_streaks
GROUP BY actor, actorid, streak_identifier, is_active, quality_class
ORDER BY actorid, streak_identifier