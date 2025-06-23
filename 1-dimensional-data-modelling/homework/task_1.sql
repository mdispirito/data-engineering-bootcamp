-- Task 1, Set up the actors table

CREATE TYPE film AS (
	film TEXT,
	votes INTEGER,
	rating FLOAT,
	filmid TEXT
);

CREATE TYPE quality_class AS
	ENUM ('star', 'good', 'average', 'bad');

CREATE TABLE actors (
	actorid TEXT,
	actor TEXT,
	films film[],
	quality_class quality_class,
	is_active BOOLEAN,
	current_year INTEGER,
	PRIMARY KEY (actorid)
);
