/*
A query that does state change tracking for players
    A player entering the league should be New
    A player leaving the league should be Retired
    A player staying in the league should be Continued Playing
    A player that comes out of retirement should be Returned from Retirement
    A player that stays out of the league should be Stayed Retired
*/

CREATE TABLE players_state_tracking (
	player_name TEXT,
	first_active_season INTEGER,
	last_active_season INTEGER,
	yearly_active_state TEXT,
	seasons_active INTEGER[],
	season INTEGER,
	PRIMARY KEY (player_name, season)
)

---
INSERT INTO players_state_tracking
WITH last_season AS (
    SELECT *
    FROM players_state_tracking
    WHERE season = 2018
), this_season AS (
    SELECT
        player_name,
        season,
        COUNT(1)
    FROM player_seasons
    WHERE season = 2019
      AND player_name IS NOT NULL
    GROUP BY player_name, season
)
SELECT
    COALESCE(ts.player_name, ls.player_name) AS player_name,
    COALESCE(ls.first_active_season, ts.season) AS first_active_season,
    COALESCE(ts.season, ls.last_active_season) AS last_active_season,
    CASE 
        WHEN ts.player_name IS NOT NULL AND ls.player_name IS NULL THEN 'New'
        WHEN ts.player_name IS NULL AND ls.player_name IS NOT NULL THEN 'Retired'
        WHEN ts.player_name IS NOT NULL AND ls.player_name IS NOT NULL AND ls.last_active_season < ts.season - 1 THEN 'Returned from Retirement'
        WHEN ts.player_name IS NOT NULL AND ls.player_name IS NOT NULL AND ls.last_active_season = ts.season - 1 THEN 'Continued Playing'
        ELSE 'Stayed Retired'
    END AS yearly_active_state,
    COALESCE(ls.seasons_active, ARRAY[]::INTEGER[])
        || CASE 
            WHEN ts.player_name IS NOT NULL THEN ARRAY[ts.season]
            ELSE ARRAY[]::INTEGER[]
        END AS seasons_active,
    COALESCE(ts.season, ls.season + 1) AS season
FROM this_season ts
FULL OUTER JOIN last_season ls
  ON ts.player_name = ls.player_name;