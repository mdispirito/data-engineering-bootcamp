-- A `datelist_int` generation query. Convert the `device_activity_datelist` column into a `datelist_int` column 

WITH user_devices AS (
	SELECT *
	FROM user_devices_cumulated
	WHERE date = DATE('2023-01-31')
), series AS (
	SELECT * 
	FROM generate_series(DATE('2023-01-01'), DATE('2023-01-31'), INTERVAL '1 day') AS series_date
), placeholder_ints AS (
	SELECT
		CASE
			WHEN device_activity @> ARRAY [DATE(series_date)]
			-- in user_devices_cumulated, we have an array of all dates that a user's device is active
			-- the following converts each of those dates into integer values that are powers of 2
			THEN CAST(POW(2, 32 - (date - DATE(series_date))) AS BIGINT)
			ELSE 0
		END placeholder_int_value,
		*
	FROM user_devices
	CROSS JOIN series
)
SELECT
	user_id,
	device_id,
	browser_type,
	CAST(CAST(SUM(placeholder_int_value) AS BIGINT) AS BIT(32)),
	BIT_COUNT(CAST(CAST(SUM(placeholder_int_value) AS BIGINT) AS BIT(32))) > 0
		AS dim_is_monthly_active,
	BIT_COUNT(CAST('11111110000000000000000000000000' AS BIT(32)) &
	CAST(CAST(SUM(placeholder_int_value) AS BIGINT) AS BIT(32))) > 0
		AS dim_is_weekly_active
FROM placeholder_ints
GROUP BY user_id, device_id, browser_type