from pyspark.sql import SparkSession
from pyspark.sql.functions import expr, col, broadcast, approx_count_distinct

"""
Create a Spark job that...
Disabled automatic broadcast join with spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
"""
# Task 1 
spark = SparkSession.builder \
    .appName("SparkMatchHomework") \
    .config("spark.sql.autoBroadcastJoinThreshold", "-1") \
    .config("spark.sql.repl.eagerEval.enabled", True) \
    .getOrCreate()

cleanup = [
    "DROP TABLE IF EXISTS data.matches_bucketed",
    "DROP TABLE IF EXISTS data.match_details_bucketed",
    "DROP TABLE IF EXISTS data.medals_matches_players_bucketed",
    "DROP TABLE IF EXISTS data.medals",
    "DROP TABLE IF EXISTS data.medals",
]

for dt in cleanup:
    spark.sql(dt)

"""
Get all the tables set up for the next task
"""

matches_bucketed_ddl = """
CREATE TABLE IF NOT EXISTS data.matches_bucketed (
    match_id STRING,
    mapid STRING,
    is_team_game BOOLEAN,
    playlist_id STRING,
    game_variant_id STRING,
    is_match_over BOOLEAN,
    completion_date TIMESTAMP,
    match_duration STRING,
    game_mode STRING,
    map_variant_id STRING
)
USING iceberg
PARTITIONED BY (days(completion_date), bucket(16, match_id));
"""

match_details_bucketed_ddl = """
CREATE TABLE IF NOT EXISTS data.match_details_bucketed (
    match_id STRING,
    player_gamertag STRING,
    previous_spartan_rank INT,
    spartan_rank INT,
    previous_total_xp INT,
    total_xp INT,
    previous_csr_tier INT,
    previous_csr_designation INT,
    previous_csr INT,
    previous_csr_percent_to_next_tier INT,
    previous_csr_rank INT,
    current_csr_tier INT,
    current_csr_designation INT,
    current_csr INT,
    current_csr_percent_to_next_tier INT,
    current_csr_rank INT,
    player_rank_on_team INT,
    player_finished BOOLEAN,
    player_average_life STRING,
    player_total_kills INT,
    player_total_headshots INT,
    player_total_weapon_damage DOUBLE,
    player_total_shots_landed INT,
    player_total_melee_kills INT,
    player_total_melee_damage DOUBLE,
    player_total_assassinations INT,
    player_total_ground_pound_kills INT,
    player_total_shoulder_bash_kills INT,
    player_total_grenade_damage DOUBLE,
    player_total_power_weapon_damage DOUBLE,
    player_total_power_weapon_grabs INT,
    player_total_deaths INT,
    player_total_assists INT,
    player_total_grenade_kills INT,
    did_win INT,
    team_id INT
)
USING iceberg
PARTITIONED BY (bucket(16, match_id));
"""

medals_matches_players_bucketed_ddl = """
CREATE TABLE IF NOT EXISTS data.medals_matches_players_bucketed (
    match_id STRING,
    player_gamertag STRING,
    medal_id BIGINT,
    count INT
)
USING iceberg
PARTITIONED BY (bucket(16, match_id));
"""

medals_ddl = """
CREATE TABLE IF NOT EXISTS data.medals (
    medal_id BIGINT,
    sprite_uri STRING,
    sprite_left INT,
    sprite_top INT,
    sprite_sheet_width INT,
    sprite_sheet_height INT,
    sprite_width INT,
    sprite_height INT,
    classification STRING,
    medal_description STRING,
    medal_name STRING,
    difficulty INT
)
USING iceberg;
"""

maps_ddl = """
CREATE TABLE IF NOT EXISTS data.maps (
    mapid STRING,
    map_name STRING,
    map_description STRING
)
USING iceberg;
"""

spark.sql(matches_bucketed_ddl)
spark.sql(match_details_bucketed_ddl)
spark.sql(medals_matches_players_bucketed_ddl)
spark.sql(medals_ddl)
spark.sql(maps_ddl)

"""
Bucket join match_details, matches, and medal_matches_players on match_id with 16 buckets,
Explicitly broadcast JOINs medals and maps
"""

# read in all files to dataframes
matches_df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv("/home/iceberg/data/matches.csv")

match_details_df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv("/home/iceberg/data/match_details.csv")

medals_matches_players_df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv("/home/iceberg/data/medals_matches_players.csv")

medals_df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv("/home/iceberg/data/medals.csv")

maps_df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv("/home/iceberg/data/maps.csv")

# rename conflicting columns
medals_df = medals_df.withColumnsRenamed({"description": "medal_description", "name": "medal_name"})
maps_df = maps_df.withColumnsRenamed({"description": "map_description", "name": "map_name"})

# write the big dataframes out to tables with 16 buckets
matches_df.write \
    .mode("overwrite") \
    .bucketBy(16, "match_id") \
    .saveAsTable("data.matches_bucketed")

match_details_df.write \
    .mode("overwrite") \
    .bucketBy(16, "match_id") \
    .saveAsTable("data.match_details_bucketed")

medals_matches_players_df.write \
    .mode("overwrite") \
    .bucketBy(16, "match_id") \
    .saveAsTable("data.medals_matches_players_bucketed")

medals_df.write \
    .mode("overwrite") \
    .saveAsTable("data.medals")

maps_df.write \
    .mode("overwrite") \
    .saveAsTable("data.maps")

# read back the bucketed tables
matches_bucketed = spark.table("data.matches_bucketed")
match_details_bucketed = spark.table("data.match_details_bucketed")
medals_matches_players_bucketed = spark.table("data.medals_matches_players_bucketed")
medals_table = spark.table("data.medals")
maps_table = spark.table("data.maps")

# join the big tables first, then broadcast join the two small dataframes
result = matches_bucketed \
    .join(match_details_bucketed, "match_id") \
    .join(medals_matches_players_bucketed, ["match_id", "player_gamertag"]) \
    .join(broadcast(medals_df), "medal_id") \
    .join(broadcast(maps_df), "mapid")

"""
With the aggregated data set
Try different .sortWithinPartitions to see which has the smallest data size (hint: playlists and maps are both very low cardinality)
"""
# Interestingly, the best compression I can get seems to be by using match_id and player_gamertag in that specific order,
# not the lower cardinality fields of mapid and playlist_id.
sorted_result = result.repartition(10, col("completion_date")) \
    .sortWithinPartitions(
        col("match_id"), # 19127 values
        col("player_gamertag"), # 63653 values
        # col("completion_date"), # 265 values
        # col("medal_id") # 138 values
        # col("mapid"), # 16 values
        # col("playlist_id"), # 24 values
    )

sorted_result.write \
    .mode("overwrite") \
    .option("write.format.default", "iceberg") \
    .saveAsTable("data.match_analysis_result_sorted")

"""
Analysis performed with query
    SELECT SUM(file_size_in_bytes) as size, COUNT(1) as num_files
    FROM data.match_analysis_result_sorted.files

Table size in bytes:
    with no sorting
        20100943
    playlist_id, mapid
        19932431
    mapid, playlist_id, medal_id, completion_date, match_id, player_gamertag (lowest cardinality to highest, this is bad)
        23189866
    player_gamertag, match_id, completion_date, medal_id, playlist_id, mapid (highest cardinality to lowest)
        19734497
    match_id, player_gamertag
        18040545
    match_id, player_gamertag, medal_id, playlist_id
        17999848
"""

"""
Aggregate the joined data frame to figure out questions like:
    Which player averages the most kills per game?
    Which playlist gets played the most?
    Which map gets played the most?
    Which map do players get the most Killing Spree medals on?
"""

# most kills per game: DanZ R3van DowN, average 42.4 kills over 5 games
kills_per_game = spark.sql("""
    SELECT player_gamertag, 
           AVG(player_total_kills) as avg_kills_per_game,
           COUNT(DISTINCT match_id) as games_played
    FROM data.match_analysis_result_sorted 
    GROUP BY player_gamertag
    HAVING games_played >= 5  -- require they've played at least 5 games
    ORDER BY avg_kills_per_game DESC
    LIMIT 5
""")

# most played playlist: id f72e0ef0-7c4a-4307-af78-8e38dac3fdba, played in 7640 matches
most_played_playlist = spark.sql("""
    SELECT playlist_id, 
           COUNT(DISTINCT match_id) as total_matches
    FROM data.match_analysis_result_sorted 
    GROUP BY playlist_id
    ORDER BY total_matches DESC
""")

# most played map: Breakout Arena, played in 7640 matches
most_played_map = spark.sql("""
    SELECT map_name, 
           COUNT(DISTINCT match_id) as total_matches
    FROM data.match_analysis_result_sorted 
    GROUP BY map_name
    ORDER BY total_matches DESC
""")

# map players get the most Killing Spree medals on: Breakout Arena, 6738 medals on that map
killing_spree_by_map = spark.sql("""
    SELECT map_name,
           SUM(count) as total_killing_spree_medals
    FROM data.match_analysis_result_sorted 
    WHERE medal_name = 'Killing Spree'
    GROUP BY map_name
    ORDER BY total_killing_spree_medals DESC
""")

# results
kills_per_game.show()

most_played_playlist.show(20, False)

most_played_map.show()

killing_spree_by_map.show()
