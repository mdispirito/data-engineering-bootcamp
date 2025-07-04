Where can you catch quality bugs?
- in development - best case
- if you're doing WAP (write, audit, publish)
	- if you write to your staging tables, then your audit fails, you have to troubleshoot the bug in your staging table
	- this is better than making it all the way to prod, but it can be time consuming, and when you have tons of false positive checks it can eat up a lot of resources
	- this also causes a data delay and impact downstream users
- in prod, in production tables - worst case
	- usually an end-user asks you why something looks weird
	- this destroys trust

How do you catch bugs in development?
- unit tests and integration tests for your pipelines!
- for example, if you have UDFs or custom functions in your spark code, ensure they are tested
	- especially if these functions call another library
	- the maintainers of other libraries can always change their code and break your tests. so your unit tests allow you to safely depend on other people's code.

How do you catch bugs in prod?
- use the write-audit-publish pattern!
	- this works by you writing to your staging table that has the same schema as production, then you run your quality checks, if they pass you move your staging data into production
- there's also another pattern called "the signal table pattern" that is preferred by some companies

Quality standards in different roles
- typically, software engineering (especially at big tech) has higher quality standards than data engineering
	- going forward, data engineering will need to adopt a lot of the quality standards of software engineering
- Why?
	- Risks
		- a lot of the times with data, it's "okay" if things break even for a day or two, depending on the use case
		- but for example if facebook's user-facing app goes down, there is a massive disruption to the business' revenue
		- as data engineers, we need to hold ourselves to higher standards of quality to open up more opportunities
	- maturation
		- software engineering is a more mature field
		- test-driven development and behaviour-driven development are very new to data engineering
	- talent
		- data engineers typically come from more diverse backgrounds, so they may have less software engineering fundamentals
			- just like everything, there are pros and cons to this reality

How does data engineering become riskier?
- we should always be asking "what is the consequence of my pipeline breaking"
- data delays impact machine learning
	- for example, at AirBnb most hosts let a "smart pricing" model determine their pricing
		- in that specific case, the training data being delayed by a day or two resulted in a drop in click-through rates and effectiveness
- data quality bugs impact experimentation
	- when data scientists are running A/B tests, they may come to the wrong conclusions!
- as trust rises in data, risk rises too
	- as companies become more and more "data driven", data engineers are carrying more weight and need to hold themselves to higher standards to uphold that level of trust

Why do companies miss the mark on data quality?
- data analytics does not have a culture of automated excellence
- facebook example: culture of "move fast and break things" put a lot of pressure on data teams to answer questions as quickly as possible
- for an alarming number of organizations, "this chart looks weird" is enough
	- at a long enough horizon, data quality and speed are not competing! you can move faster by having more quality checks and "doing things right"

Tradeoff between business velocity and "sustainability/quality"
- the business wants answers fast
- engineers don't want to die from a mountain of tech debt
- who wins? it usually depends on the strength of your engineering leaders and their ability to push back!
- if you don't cut corners you can move forward in a more sustainable fashion
	- it's always context-dependent, but it should be a high bar for justifying corner-cutting
- data engineers are not just answering questions, they're building "roads and highways for information"
	- you can build a dirt road a lot faster, but...

Data engineering capability standards will increase over time
- latency
	- solved with streaming pipelines and microbatch pipelines
	- for things like fraud detection and dynamic pricing, you need data available sooner!
- quality
	- solved with frameworks like Great Expectations, amazon deequ, or other best practices
- completeness
	- solved through communication and understanding the complete domain
	- you want to work with people that are close to the business to build your understanding
- ease-of-access and accessibility
	- solved by data products and proper data modelling
	- data engineers typically think of their product as just a table that users can run SQL on, or a dashboard that users can apply filters to
		- however there is a ton more that you can do, like surfacing data through APIs for easier integration

How to adopt a Software Engineering Mindset as a DE
- code is 90% read by humans and 10% run by machines
	- avoid things like "if i do 5 subqueries it's 5% faster than if I use 2 CTEs"
		- how much pain and suffering are you causing fellow engineers though?
- silent failures are your enemy
- loud failures are your friend
	- fail the data when bata data is introduced
	- loud failures are accomplished by testing and CI/CD
		- best case scenario you have custom exceptions like a `DuplicateRecordException` for example - use these in your pipelines!
- DRY code and YAGNI principle
	- SQL and DRY can be combative
- design documents are your friend
- care about efficiency
	- pay attention to DSA, joins and shuffles, etc
- if you don't want to learn these things
	- go into analytics engineering :) 
