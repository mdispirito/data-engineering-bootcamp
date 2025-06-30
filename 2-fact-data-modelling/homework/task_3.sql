-- A cumulative query to generate `device_activity_datelist` from `events`

/*
My main concern at first was getting the correct device_id and browser_type combo for each event,
given that the devices table has no PK constraint, and it seemed reasonable that you could have
a one-to-many relationship between devices and browser_types. However upon inspecting the devices table,
it appears that device_id, browser_type is basically a composite PK and there is only one record
for each of those pairs (when you remove duplicates).
 */

INSERT INTO user_devices_cumulated
WITH yesterday AS (
	SELECT *
	FROM user_devices_cumulated
	WHERE date = DATE('2022-12-31')
), today AS (
	SELECT
		CAST(e.user_id AS TEXT) AS user_id,
		CAST(e.device_id AS TEXT) AS device_id,
		d.browser_type as browser_type,
		DATE(CAST(event_time AS TIMESTAMP)) AS date_active
	FROM events e
	JOIN devices d ON d.device_id = e.device_id
	WHERE DATE(CAST(event_time AS TIMESTAMP)) = DATE('2023-01-01')
	AND e.user_id IS NOT NULL
	AND e.device_id IS NOT NULL
	GROUP BY e.user_id, e.device_id, d.browser_type, DATE(CAST(event_time AS TIMESTAMP))
)
SELECT
	COALESCE(t.user_id, y.user_id) AS user_id,
	COALESCE(t.device_id, y.device_id) AS device_id,
	COALESCE(t.browser_type, y.browser_type) as browser_type,
	CASE
		WHEN y.device_activity IS NULL
			THEN ARRAY[t.date_active]
		WHEN t.date_active IS NULL
			THEN y.device_activity
		ELSE ARRAY[t.date_active] || y.device_activity
	END AS device_activity,
	COALESCE(t.date_active, y.date + INTERVAL '1 day') AS date
FROM today t
FULL OUTER JOIN yesterday y
ON t.user_id = y.user_id AND t.device_id = y.device_id AND t.browser_type = y.browser_type