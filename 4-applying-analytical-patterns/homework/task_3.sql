/*
A query that uses window functions on game_details to find out the following things:
    - What is the most games a team has won in a 90 game stretch?
*/

WITH all_team_games AS (
    SELECT
        game_id,
        game_date_est,
        home_team_id AS team_id,
        CASE WHEN home_team_wins = 1 THEN 1 ELSE 0 END AS win
    FROM games
    UNION ALL
    SELECT
        game_id,
        game_date_est,
        visitor_team_id AS team_id,
        CASE WHEN home_team_wins = 0 THEN 1 ELSE 0 END AS win
    FROM games
),
ordered_team_games AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY team_id ORDER BY game_date_est) AS game_num
    FROM all_team_games
),
rolling_wins AS (
    SELECT
        team_id,
        game_id,
        game_date_est,
        SUM(win) OVER (
            PARTITION BY team_id
            ORDER BY game_num
            ROWS BETWEEN CURRENT ROW AND 89 FOLLOWING
        ) AS wins_in_90_games
    FROM ordered_team_games
),
team_max_90_win_streaks AS (
    SELECT
        team_id,
        MAX(wins_in_90_games) AS max_wins_in_90_game_span
    FROM rolling_wins
    GROUP BY team_id
)
SELECT *
FROM team_max_90_win_streaks
ORDER BY max_wins_in_90_game_span DESC