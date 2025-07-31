-- Compare results between different hosts (zachwilson.techcreator.io, zachwilson.tech, lulu.techcreator.io)
select host, avg(num_hits) avg_session_hits
from processed_events_aggregated
group by host
order by avg_session_hits desc;

-- results: after running the job for about 25 minutes, the avg number of web events from hosts are as follows:
-- learn.dataexpert.io:     3.2
-- www.dataexpert.io:       2.1