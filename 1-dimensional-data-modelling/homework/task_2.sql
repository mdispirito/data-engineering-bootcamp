-- Task 2: write a query that populates the actors table one year at a time.
-- the first year in actor_films is 1970,
-- so that's what we use in our `this_year` CTE
WITH last_year AS (
	SELECT * FROM actors
	WHERE current_year = 1969
), this_year AS (
    SELECT 
        actorid,
        actor,
        year,
        ARRAY_AGG(ROW(
            film,
            votes,
            rating,
            filmid
        )::film) AS films,
        AVG(rating) AS avg_rating
    FROM actor_films
    WHERE year = 1970
    GROUP BY actorid, actor, year
)

INSERT INTO actors
SELECT
	COALESCE(ly.actorid, ty.actorid) AS actorid,
	COALESCE(ly.actor, ty.actor) AS actor,
    COALESCE(ly.films, ARRAY[]::film[]) || COALESCE(ty.films, ARRAY[]::film[]) AS films,
	CASE
		WHEN ty.year IS NOT NULL THEN (
			CASE
				WHEN ty.avg_rating > 8 THEN 'star'
				WHEN ty.avg_rating > 7 THEN 'good'
				WHEN ty.avg_rating > 6 THEN 'average'
				ELSE 'bad'
			END
		)::quality_class
		ELSE ly.quality_class
	END AS quality_class,
	ty.actorid IS NOT NULL AS is_active,
	1970 AS current_year
	
FROM last_year ly
FULL OUTER JOIN this_year ty
ON ly.actorid = ty.actorid