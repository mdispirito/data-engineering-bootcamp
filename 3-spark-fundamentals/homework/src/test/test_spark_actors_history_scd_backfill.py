from chispa.dataframe_comparer import *
from ..jobs.spark_actors_history_scd_backfill import do_actors_history_scd_backfill_transformation
from collections import namedtuple
from pyspark.sql.functions import col

Actor = namedtuple("Actor", "actorid actor current_year quality_class is_active")
ActorHistoryScd = namedtuple("ActorHistoryScd", "actorid actor quality_class is_active start_date end_date current_year")


def test_actors_scd_generation(spark):
    source_data = [
        Actor("actor1", "Leonardo DiCaprio", 2019, "star", True),
        Actor("actor1", "Leonardo DiCaprio", 2020, "star", True),
        Actor("actor1", "Leonardo DiCaprio", 2021, "good", True),
        Actor("actor2", "Tom Hanks", 2020, "good", True),
        Actor("actor2", "Tom Hanks", 2021, "good", False),
        Actor("actor3", "Brad Pitt", 2021, "average", True)
    ]
    source_df = spark.createDataFrame(source_data)

    actual_df = do_actors_history_scd_backfill_transformation(spark, source_df)
    
    expected_data = [
        ActorHistoryScd("actor1", "Leonardo DiCaprio", "star", True, 2019, 2020, 2021),
        ActorHistoryScd("actor1", "Leonardo DiCaprio", "good", True, 2021, 2021, 2021),
        ActorHistoryScd("actor2", "Tom Hanks", "good", True, 2020, 2020, 2021),
        ActorHistoryScd("actor2", "Tom Hanks", "good", False, 2021, 2021, 2021),
        ActorHistoryScd("actor3", "Brad Pitt", "average", True, 2021, 2021, 2021)
    ]
    expected_df = spark.createDataFrame(expected_data)
    # in the source query we hardcode current_year which spark interprets as an IntegerType
    # so we need to cast it in the output to match
    expected_df = expected_df.withColumn("current_year", col("current_year").cast("int"))
    
    assert_df_equality(actual_df, expected_df, ignore_row_order=True, ignore_nullable=True)
