from chispa.dataframe_comparer import *
from ..jobs.spark_user_devices_cumulated import do_user_devices_cumulated_transformation
from collections import namedtuple
from pyspark.sql.functions import col
from pyspark.sql.types import *
import pytest
import os
from pyspark.sql import SparkSession
from datetime import date


Event = namedtuple("Event", "user_id device_id event_time")
Device = namedtuple("Device", "device_id browser_type")
UserDevicesCumulated = namedtuple("UserDevicesCumulated", "user_id device_id browser_type device_activity date")
UserDevicesCumulatedExpected = namedtuple("UserDevicesCumulatedExpected", "user_id device_id browser_type device_activity date")


def test_user_devices_cumulated_generation(spark):
    # event data for the current day, 2023-01-01
    events_data = [
        Event("user1", "device1", "2023-01-01 10:00:00"),
        Event("user1", "device2", "2023-01-01 11:00:00"),
        Event("user2", "device1", "2023-01-01 12:00:00")
    ]
    events_df = spark.createDataFrame(events_data)
    events_df.createOrReplaceTempView("events")
    
    # devices data
    devices_data = [
        Device("device1", "Chrome"),
        Device("device2", "Firefox")
    ]
    devices_df = spark.createDataFrame(devices_data)
    devices_df.createOrReplaceTempView("devices")
    
    # previous day's cumulated data, 2022-12-31
    yesterday_data = [
        UserDevicesCumulated("user1", "device1", "Chrome", [date(2022, 12, 30)], date(2022, 12, 31)),
        UserDevicesCumulated("user2", "device3", "Safari", [date(2022, 12, 31)], date(2022, 12, 31))
    ]
    yesterday_df = spark.createDataFrame(yesterday_data)
    yesterday_df.createOrReplaceTempView("user_devices_cumulated")

    actual_df = do_user_devices_cumulated_transformation(spark, events_df, "2023-01-01")
    
    expected_data = [
        UserDevicesCumulatedExpected("user1", "device1", "Chrome", [date(2023, 1, 1), date(2022, 12, 30)], date(2023, 1, 1)),
        UserDevicesCumulatedExpected("user1", "device2", "Firefox", [date(2023, 1, 1)], date(2023, 1, 1)),
        UserDevicesCumulatedExpected("user2", "device1", "Chrome", [date(2023, 1, 1)], date(2023, 1, 1)),
        UserDevicesCumulatedExpected("user2", "device3", "Safari", [date(2022, 12, 31)], date(2023, 1, 1))
    ]
    expected_df = spark.createDataFrame(expected_data)
    
    assert_df_equality(actual_df, expected_df, ignore_row_order=True, ignore_nullable=True)


def test_user_devices_cumulated_new_user(spark):
    # brand new user
    events_data = [
        Event("new_user", "device1", "2023-01-01 10:00:00")
    ]
    events_df = spark.createDataFrame(events_data)
    events_df.createOrReplaceTempView("events")
    
    devices_data = [
        Device("device1", "Chrome")
    ]
    devices_df = spark.createDataFrame(devices_data)
    devices_df.createOrReplaceTempView("devices")
    
    # schema for yesterday's data, which we assume is empty
    yesterday_schema = StructType([
        StructField("user_id", StringType(), True),
        StructField("device_id", StringType(), True),
        StructField("browser_type", StringType(), True),
        StructField("device_activity", ArrayType(DateType(), True), True),
        StructField("date", DateType(), True)
    ])
    yesterday_df = spark.createDataFrame([], yesterday_schema)
    yesterday_df.createOrReplaceTempView("user_devices_cumulated")

    actual_df = do_user_devices_cumulated_transformation(spark, events_df, "2023-01-01")
    
    expected_data = [
        UserDevicesCumulatedExpected("new_user", "device1", "Chrome", [date(2023, 1, 1)], date(2023, 1, 1))
    ]
    expected_df = spark.createDataFrame(expected_data)
    
    assert_df_equality(actual_df, expected_df, ignore_row_order=True, ignore_nullable=True)
