/*
A query that uses GROUPING SETS to do efficient aggregations of game_details data
    Aggregate this dataset along the following dimensions
    - player and team
        - Answer questions like who scored the most points playing for one team?
    - player and season
        - Answer questions like who scored the most points in one season?
    - team
        - Answer questions like which team has won the most games?
*/

SELECT
	COALESCE(player_name, '(overall)') AS player_name,
	COALESCE(team_abbreviation, '(overall)') AS team_abbreviation,
	season,
	SUM(pts) AS points_scored,
	SUM(CASE WHEN 
			(team_id = team_id_home AND home_team_wins = 1) OR
			(team_id = team_id_away AND home_team_wins = 0) THEN 1 ELSE 0 
		END
	) AS games_won
FROM game_details gt
JOIN games g ON gt.game_id = g.game_id
GROUP BY GROUPING SETS (
	(player_name, team_abbreviation),
	(player_name, season),
	(team_abbreviation)
)
ORDER BY points_scored DESC