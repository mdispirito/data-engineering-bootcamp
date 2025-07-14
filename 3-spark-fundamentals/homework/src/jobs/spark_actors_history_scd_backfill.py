from pyspark.sql import SparkSession

# Query from Week 1 Task 4
query = """

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
            WHEN previous_quality_class IS NULL THEN 1
            WHEN quality_class != previous_quality_class THEN 1
            WHEN previous_is_active IS NULL THEN 1
            WHEN is_active != previous_is_active THEN 1
            ELSE 0
        END AS change_indicator
    FROM with_previous
),
with_streaks AS (
    SELECT *,
        SUM(change_indicator) OVER (PARTITION BY actorid ORDER BY current_year ROWS UNBOUNDED PRECEDING) AS streak_identifier
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

"""


def do_actors_history_scd_backfill_transformation(spark, dataframe):
    dataframe.createOrReplaceTempView("actors")
    return spark.sql(query)


def main():
    spark = SparkSession.builder \
      .master("local") \
      .appName("actors_history_scd_backfill") \
      .getOrCreate()

    output_df = do_actors_history_scd_backfill_transformation(spark, spark.table("actors"))
    output_df.write.mode("overwrite").insertInto("actors_history_scd")
