Is it a fact or a dimension?
- did a user log in today?
	- the log in event would be a fact that informs the "dim_is_active" dimension
		- but if the dimension is based on an event, like whether a user liked/commented/shared, is it a dimension or just an aggregation of facts?
			- ... it's both
	- vs. the state "dim_is_activated" (when a user deactivates or activates their account) which is state-driven, not activity-driven
		- this is purely a dimension
		- but there's also the event of you going and changing the value, that is a fact
- you can aggregate facts and turn them into dimensions
	- you want to think about what the cardinality of the dimension is
		- ex. if i had 17 likes on facebook, it's not useful to look at everyone that had 17 likes. you maybe want to pick a bucket of 10 or 20
	- ex. is this person a "high engager" or a "low engager"?
	- `CASE WHEN` to bucketize aggregated facts can be useful to reduce the cardinality
	- also, if you end up with data that has "groups of 1" because of too much cardinality, you lose a lot of predictive power
- how you bucketize needs to be informed. you need to look at the distribution of the data

Properties of facts vs. dimensions
- Dimensions
	- they usually show up in the `GROUP BY` when doing analytics
		- userID, device, gender, country, etc
	- can be high or low cardinality
	- they generally come from a snapshot of state
- Facts
	- these are the things you aggregate with `SUM`, `AVG`, `COUNT`
	- almost always higher volume than dimensions, although some fact sources are low-volume (like rare events)
		- usually the number of "things" a user can do is quite numerous
	- generally come from events and logs
- Change Data Capture (CDC) is an example of the blurry line between facts and dimensions
	- you basically model a state change of a dimension as a fact
- a blurry example from Airbnb
	- is the price of a night on airbnb a fact or dimension?
	- the host can set the price which sounds like an event
	- it's kind of rare for a decimal number to be a dimension
	- however in this case it is a dimension, because it's an attribute of the night
	- the fact in this case would be the host changing the setting that impacted the price (ex. early bird discount)
	- a fact has to be logged, a dimension comes from the state of things
	- price being derived from settings is a dimension

Boolean/Existence-based Facts and Dimensions
- `dim_is_active`, `dim_bought_something`
	- these are usually on the daily/hourly grain
- `dim_has_ever_booked`, `dim_ever_active`, `dim_ever_labelled_fake`
	- these "ever" dimensions look to see if there has ever been a log and once it flips one way, it never goes back
	- these are powerful features for machine learning
		- ex. an airbnb host with active listings who has never been booked
- "days since" dimensions (ex. `days_since_last_active`, `days_since_signup`)
	- very common in retention analytical patterns

Categorical Facts/Dimensions
- "scoring_class" in week 1
	- a dimension derived from fact data
- often calculated with `CASE WHEN` logic and bucketizing
	- example: airbnb superhosts are based on a whole bunch of columns
		- certain amount of ratings, bookings, revenue, etc

Should you use dimensions or facts to analyze users?
- is the `dim_is_activated` state or `dim_is_active` logs a better metric?
	- it probably depends! both are useful

The extremely efficient DateList data structure
- a common question at facebook at other companies is: how many MAU? weekly? daily?
	- monthly is hard to process because you have to look at the last 30 days of facts which is a massive amount of data.
	- the naive approach is every day, look at the last 30 days of data and see if they were active on at least one of the days
- Imagine a cumulated schema like `users_cumulated`
	- user_id
	- date
	- dates_active: an array of all the recent days that a user was active
	- downside of this is you have a huge array of dates
- Instead, you can turn that into a structure like this
	- user_id, date, datelist_int
	- user01, 2023-01-01, 100000010000001
	- where the 1s in the integer represent the activity for 2023-01-01 - bit position (zero indexed)
