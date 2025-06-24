What is a fact?
- something that happened or occurred, an event
	- user logs into an app
	- transaction is made
- facts are not slowly changing, which makes them easier to model in some respects

What makes modelling facts hard?
- it's usually 10x - 100x the volume of dimensional data
	- imagine facebook with 2B active users, generating hundreds of events every day
- fact data can need a lot of context for effective analysis
	- for example, the event "sent a notification" in isolation is pretty useless
	- but, "sent notification" -> "clicked something" -> "bought something" is very valuable
	- when working with facts, you need to ask "what other fact or dimension data do we need to make this more useful"
- duplicates in facts are way more common than in dimensional data
	- you could have bugs in the application causing duplications
	- you could also have valid duplicates, like a user clicking the same notification twice at different times

How does fact data modelling work?
- Normalization vs.  Denormalization
	- Normalized facts don't have dimensional attributes, just IDs
		- ex. "userID 100 logged in at this date"
	- Denormalized facts bring in some dimensional attributes for quicker analysis at the cost of more storage
		- ex "30 year old male in canada logged in at this date"
	- there is a tradeoff between the two
	- at a smaller scale normalization is usually beneficial
- fact data and raw logs are not the same thing
	- even though logging and fact data are linked closely
	- raw logs
		- ugly schemas designed for online systems that usually make analysis hard
		- potentially contain duplicates or quality errors
		- usually have shorter retention
	- fact data
		- nicer column names
		- quality guarantees like uniqueness, not null,  etc,
		- longer retention
	- trust in fact data should be much higher than in raw logs

Who, What, When, Where, How
- "Who" fields are usually pushed out as IDs
	- userIDs, deviceIDs
- "Where" fields
	- could be location
	- could be "where in the app" for example (home page, profile page, etc)
	- can also be modelled as IDs, but usually not
- "How" fields
	- usually similar to "where" fields in a virtual worlds
	- ex, "used an iphone to make this click". is the iphone the where or how?
- "What" fields
	- the actual event itself
	- in the notification world, "generated", "sent", "clicked", "delivered"
	- usually think of these as atomic events and not higher level
		- example running one step vs running one mile
- "When" fields
	- almost always "event_timestamp" or "event_date"

Fact data modelling continued
- fact datasets should have quality guarantees
	- certain fields should not be nullable
- fact data should generally be smaller than raw logs
- fact data should parse out hard-to-understand columns
	- there should not be many complex data types

When should you model in dimensions?
- an example Zach gives is working at Netflix when they had 3000 microservices and needed to understand which ones talked to which others for security purposes
- they built the initial pipeline using a relatively small table of internal IPs that could be joined with app names using a broadcast join, so it worked
- but when they needed to upgrade to IPv6 and the range of IPs went up, a broadcast join no longer worked
- the only solution was to have each app owner (all 3000 of them) essentially add the app name to all of their logs, effectively denormalizing the log data and making it so the join never needed to happen at all

How does logging fit into fact data?
- logging brings in all the critical context for your fact data
	- usually done in collaboration with the SWEs working on online apps
- do NOT log everything, only what you need
	- raw logs can be very expensive
- logging should confirm to values specified by online teams
	- ex. Thrift is a language-agnostic specification, can be used for example by a ruby team and scala team to reference the same schema

Options when working with high volume fact data
- Sampling
	- doesn't work for all use cases
	- but something the best solution is to just leave some of the data out
	- security is an example use case where sample would not work
- Bucketing
	- bucket by one of the most important dimensions (usually "who", or user)
	- bucket joins can be much faster than shuffle joins
	- sorted-merge bucket (SMB) joins can do joins without shuffle at all

How long should you hold on to fact data?
- high volumes make it costly to hold on to
- usually after 60 - 90 days, data is moved to a new table with PII stripped
- all depends on company size and budget, but the bigger the table, the shorter the retention usually
	- always be thinking "what is the ROI of holding on to this data?"

Deduplication of fact data
- facts can often be duplicated and it could be valid
- you need to pick the right window for deduplication
- intraday deduping options
	- streaming
	- microbatching

Streaming to deduplicate facts
- allows you to capture duplicates efficiently
- large majority of duplicates usually happen in a short window after the first even
- choosing the right window does matter
- entire day duplicates can be hard for streaming because it needs to hold on to a lot in memory
- 15 min - hourly windows are usually the sweet spot

Hourly microbatch deduplication
- used to reduce landing time of daily tables that dedupe slowly
- complicated process outlined in the lecture...
