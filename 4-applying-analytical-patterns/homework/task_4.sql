/*
A query that uses window functions on game_details to find out the following things:
    - How many games in a row did LeBron James score over 10 points a game?
*/

WITH lebron_scoring AS (
    SELECT
        g.game_date_est,
        gd.game_id,
        gd.pts,
        CASE WHEN gd.pts > 10 THEN 1 ELSE 0 END AS over_10,
        ROW_NUMBER() OVER (ORDER BY g.game_date_est) AS rn,
        -- this is a cumulative sum of games where he scored more than 10 pts
        SUM(CASE WHEN gd.pts > 10 THEN 1 ELSE 0 END) OVER (ORDER BY g.game_date_est ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS streak_id
    FROM game_details gd
    JOIN games g ON gd.game_id = g.game_id
    WHERE gd.player_name = 'LeBron James'
      AND gd.min IS NOT NULL
)
SELECT MAX(streak_len) AS longest_streak_over_10_pts
FROM (
    SELECT
    	-- the difference between streak id and rn will stay constant for consecutive >10 pt games
        streak_id - rn AS group_id,
        COUNT(*) AS streak_len
    FROM lebron_scoring
    WHERE over_10 = 1
    GROUP BY streak_id - rn
) streaks;
