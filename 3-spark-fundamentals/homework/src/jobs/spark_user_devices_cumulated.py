from pyspark.sql import SparkSession
from datetime import datetime, timedelta

# Query from Week 2 Task 3
def get_query(today_date):
    today_dt = datetime.strptime(today_date, '%Y-%m-%d')
    yesterday_dt = today_dt - timedelta(days=1)
    yesterday_date = yesterday_dt.strftime('%Y-%m-%d')

    return f"""
	WITH yesterday AS (
		SELECT *
		FROM user_devices_cumulated
		WHERE date = '{yesterday_date}'
	), today AS (
		SELECT
			CAST(e.user_id AS STRING) AS user_id,
			CAST(e.device_id AS STRING) AS device_id,
			d.browser_type as browser_type,
			DATE(CAST(e.event_time AS TIMESTAMP)) AS date_active
		FROM events e
		JOIN devices d ON d.device_id = e.device_id
		WHERE DATE(CAST(e.event_time AS TIMESTAMP)) = '{today_date}'
		AND e.user_id IS NOT NULL
		AND e.device_id IS NOT NULL
		GROUP BY e.user_id, e.device_id, d.browser_type, DATE(CAST(e.event_time AS TIMESTAMP))
	)
	SELECT
		COALESCE(t.user_id, y.user_id) AS user_id,
		COALESCE(t.device_id, y.device_id) AS device_id,
		COALESCE(t.browser_type, y.browser_type) as browser_type,
		CASE
			WHEN y.device_activity IS NULL
				THEN ARRAY(t.date_active)
			WHEN t.date_active IS NULL
				THEN y.device_activity
			ELSE CONCAT(ARRAY(t.date_active), y.device_activity)
		END AS device_activity,
		COALESCE(t.date_active, DATE_ADD(y.date, 1)) AS date
	FROM today t
	FULL OUTER JOIN yesterday y
	ON t.user_id = y.user_id AND t.device_id = y.device_id AND t.browser_type = y.browser_type

	"""


def do_user_devices_cumulated_transformation(spark, dataframe, today_date):
    dataframe.createOrReplaceTempView("events")
    query = get_query(today_date)
    return spark.sql(query)


def main():
    spark = SparkSession.builder \
      .master("local") \
      .appName("user_devices_cumulated") \
      .getOrCreate()

    output_df = do_user_devices_cumulated_transformation(spark, spark.table("events"))
    output_df.write.mode("overwrite").insertInto("user_devices_cumulated")
