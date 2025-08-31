Complex metrics mean complex data models
- requests for complex metrics should usually be pushed back on
- usually best to give analysts/data scientists raw aggreates

Types of metrics
- aggregates / counts
	- swiss army knifle and most common type of metric DEs should work with
	- number of times someone has logged in, number of friends added, number of notifications responded to, etc
- ratios (survivorship, etc)
	- DEs usually supply numerators and denominators, not the ratios
	- examples: conversion rate, purchase rate, cost to acquire a customer
	- if you're owning metrics like this as a DE, you usually get dragged into business questions - maybe that's what you want though?
- percentiles
	- useful for measuring the experience at the extremes
	- examples: p99 latency (i.e. how fast is our worst experience?), p10 engagement of active users

Metrics can be "gamed" and need balance
- experiments can move metrics up short-term by down long-term
- example: notifications
	- if you send more, you get more users in the short term, but then it starts to get really annoying...
- novelty effects - example adding an emoji in notifications boosted conversion rate a ton initially, but the effect wore off gradually

How does an experiment work?
- make a hypothesis!
	- the null hypothesis (also called H naught) - there will be no difference
	- the alternative hypothesis - there is a significant difference from the changes
	- you either reject or fail to reject the null hypothesis
		- your alternative hypothesis might not be exactly right even if the null hypothesis is rejected
- group assignment (test vs control)
	- who is eligible?
		- are these users in a long-term holdout?
		- what percentage of users do we want to experiment on?
			- what if your experiment sucks and has a lot of downside? you don't want that affecting too many people
- collect data
	- until you get a statistically significant result
	- make sure to use stable identifiers
		- hash IP addresses to minimize the collection of PII
		- you can leverage stable IDs in statsig
	- the smaller the effect, the longer you'll have to wait
	- keeping in mind some effects may be so small you'll never get a statsig result
	- do not underpower your experiments
		- the more test cells you have, the more data you need to collect
		- it's unlikely you have the same data collection as google and can test 41 different shades of blue
	- collect all the events and dimensions you want to measure differences
- look at the difference between groups

Look for statistical significance
- P values - the probability that the outcome was due to random chance
- P < 0.05 is industry standard
- statistically significant results may still be useless though

Gotchas when looking for statistical significance
- when looking at count data, extreme outliers can skew the distribution the wrong way
	- winsorization helps with this
