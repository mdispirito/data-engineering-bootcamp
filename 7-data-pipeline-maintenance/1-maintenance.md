The more you build, the more maintenance cost you build up.

The difficult parts of data engineering
- building pipelines and infrastructure is a marathon, performing analysis is usually a sprint
- there is usually a push and pull between the marathon of building the data infrastructure and the sprint of performing the analysis and unlocking insights
	- say no to sprinting the marathon

Ad-hoc requests
- analytics needs to solve urgent problems, and usually everything is urgent to them
- maybe 5 - 10% of your time should be spent on ad-hoc requests
	- that equates to about half a day each week
	- low-hanging fruit can be done quickly, but otherwise it needs to go on the roadmap

Ownership models
- Most common
	- software engineers: logging and exports
	- data engineers: pipelines, master data
	- data analysts: metrics, dashboards, experimentation
- Another common pattern
	- software engineers: logging and exports
	- primary analytics engineers/spanners: pipelines, master data, metrics
		- sometimes "spanners" also own logs and dashboards - pretty much everything
	- data analysts/scientists: dashboards and experiments

Where do ownership problems arise?
- at the boundaries!
	- data engineers owning logging
	- data scientists writing pipelines
	- data engineers owning metrics
- what happens when boundaries are crossed?
	- burnout
	- bad team dynamics
	- blame game
	- bad cross-functional support

Centralized vs. Embedded Data Teams
- Centralized
	- many data engineers in one team
	- on-call is easier
	- knowledge sharing, DEs supporting DEs
	- expensive, prioritization can get complex
- Embedded
	- data engineers in other engineering teams
	- dedicated DE support, DE gains deep domain knowledge
	- islands of responsibility, DEs can feel isolated

Common issues in pipelines you're bound to face....

Skew leading to OOM
- this happens when doing a group by or join and one key has a ton more data
- best option
	- UPGRADE TO SPARK 3 and enable adaptive execution
- second best option
	- bump up the executor memory and hope it's not more skewed later
- third best option
	- update the job to include a skew join salt
		- this basically involves getting data from the same key shipped to different executors using a random number

Missing Data / Schema Change
- have pre-checks on your upstream data
	- especially if it's data from a 3rd party
		- this will prevent your pipeline from running if it's missing data
- track down the upstream owner
	- fill out a task/ticket to have them fix the issue

Backfill Triggers Downstream Pipelines
- for small migrations
	- do a parallel backfill into a table called `table_backfill` for example
	- if everything looks good, do the "shell game"
		- rename `production` to `production_old`
		- rename `table_backfill` to `production`
- if people need a lot more time to migrate (a lot more painful)
	- may need to look at this approach if you have >30 downstream pipelines, otherwise the other approach is usually best
	- build a parallel pipeline that populates `table_v2` while production gets migrated - you encourage everyone to move over to v2
	- after all references to `production` get migrated, drop production and rename `table_v2` to `production`
	- many teams omit the final step where they rename back to `production` because it's a PITA, but it can lead to messiness later

Business Questions
- set an SLA on when you'll get back to people. maybe 2 hours, maybe a day, maybe more?
- consolidate common questions into a document so you don't have to keep answering the same question
- sometimes this is not handled by the data pipeline on-call
