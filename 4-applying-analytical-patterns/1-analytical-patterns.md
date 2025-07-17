Common Patterns
- state change tracking
- survivorship analysis
- window-based analysis

Repeatable Analyses
- reduces the cognitive load of thinking about things in SQL
- languages and tools will change, so more important is to understand higher-level patterns

Aggregation-based Analyses
- this is the most common and simple type
- aggregations are all about `GROUP BY`!
- most of the time you're doing sum, avg, or count in these analyses
- usually you are bringing in dimensions (ex. country, gender, device)
- these are usually presented as line charts or bar charts
- cumulation and window-based analyses often have aggregation-based analyses on top of them
- common examples
	- root cause analysis (why is this thing happening)
	- trend analysis
	- composition
		- we have X number of users in the US, Y number in canada, etc
- things to look out for
	- think about combinations that matter the most, be careful about bringing in too many dimensions
		- once you bring in enough dimensions, you basically just get back to the daily data
		- enough dimensions put together will uniquely identify a person
	- when looking at a long time frame, you don't want to have too many cuts in your data
		- if you hold on to daily data, you can end up with a lot of rows, so you usually want to lower the cardinality by looking a time by week, month or year

Cumulation-based Analyses
- these are based on the cumulative table design from week 1
- the big ones include:
	- state transition tracking
	- retention (also called j curves or survivorship analysis)
- the main difference vs aggregation patterns is these care a lot about the relationship between today and yesterday and the change in state between those points in time
- `FULL OUTER JOIN` is your best friend with this pattern, because you need to keep track of when there *isn't* data (i.e. no data *is* data, the fact that a user did not do something is something we care about)
- Growth Accounting
	- this is a special version of state transition tracking
	- there are 5 states a user can be in:
		- new - didn't exist yesterday, active today
		- retained - active yesterday, active today
		- churned -  active yesterday, inactive today
		- resurrected - inactive yesterday, active today
		- stale - inactive yesterday, inactive today
	- sometimes you may have a 6th state such as deleted
		- many companies anonymize user data so they can keep it indefinitely
	- you can think of growth as `(new + resurrected) / churned`
	- you can apply this same state transition tracking to other use cases, such as classifying fake accounts
	- this type of pattern can give you good monitoring of your ML classification models - for example, if you see big growth in accounts getting labelled as fake, there could be an issue you need to look into

Survivorship Analysis
- this is all about measuring how many people are sticking around
- J-curves can be declining, flattening or smiling
- J-curves analyses have 3 properties: curve. | state check | reference date
	- users who stay active | activity on the app | sign up date
	- cancer patients who continue to live | not dead | diagnosis date
	- smokers who remain smoke-free after quitting | not smoking | quit date
	- boot camp attendees who keep attending | activity on zoom | enrolment date

Window-based Analyses
- Common patterns
	- DoD / WoW / MoM / YoY
		- this is a rate of change over time
	- rolling sum / average
	- ranking
- keyword with these analyses is rolling
- mostly used using window functions
```sql
FUNCTION() OVER (PARTITION BY keys ORDER BY sort ROWS BETWEEN n PRECEEDING AND CURRENT ROW)
```
- you have to be careful with time periods when doing these analyses and pay attention to the volatility in the chart
	- for example, for a hotel company using YoY metrics comparing 2021 to 2020 when the pandemic hit, it'd look like you were doing something insanely well when really it was just normal
	- using rolling averages can help with this
- big data gotchas
	- make sure to use PARTITION BY or else you'll run into OOMs on big data
