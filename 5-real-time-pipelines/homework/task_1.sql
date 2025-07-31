-- What is the average number of web events of a session from a user on Tech Creator?
select avg(num_hits) from processed_events_aggregated;

-- results: after running the job for about 25 minutes, the avg number of web events from a session is 2.7