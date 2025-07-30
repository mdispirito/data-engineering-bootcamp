Streaming needs a lot of pieces to work
- for streaming to work, you need a "live" architecture, which involves some sort of event generation layer
- for most websites, that would be an HTTP intercepter, which takes the web request and logs it to kafka before then passing it on to the web server

HTTP Intercepter Example
```javascript
export default function createAPIEventMiddleware(req, res, next) {
	const shouldBeLogged =
		req.url && !req.hostname.includes('localhost') && !isFileRequest(req);
	const event = {
		url: req.url,
		referrer: req.headers.referrer,
		user_agent: JSON.stringify(useragent.parse(req.headers['user-agent'])),
		headers: JSON.stringify(req.headers),
		host: req.headers.host,
		ip: req.connection.remoteAddress,
		event_time: new Date()
	};

	if (shouldBeLogged) {
		Promise.all([
			sendMessageToKafka({...event}),
		]).then(() => {
			next();
		})
	} else {
		next();
	}
}
```

Kafka Producer
```javascript
export default function sendMessageToKafka(message: object) {
	const producer = new Kafka.Producer({
		connectionString: process.env.KAFKA_URL,
		ssl: {cert: process.env.KAFKA_CLIENT_CERT...},
	});

	const messageObject = {
		topic: 'example.bootcamp-events',
		message: {...}
	} as Message;

	producer
		.init()
		.then(() => {
			return producer.send([messageObject])
		})
		.then((result: result) => {
			console.log('message sent', result);
			return producer.end();
		})
		.catch((err) => {
			console.error('error sending message', err);
			return producer.end();
		});
}
```

Websockets
- traditionally in web architectures, the client initiates the request to the server
- if the server gets new data, the client needs to ask for it before it can get it
- websockets allow more 2-way communication, so the server can just send new information to the client without being asked

Big Competing Architectures
- Lambda Architecture
- Kappa Architecture
- which one is used can depend on the company and their business model
	- for example, Uber is the posterchild for Kappa because they are a real-time based company

Lambda Architecture
- You essentially double the codebase - you have BOTH a batch pipeline and a streaming pipeline that write the same data
	- the batch pipeline is there as a backup
- Optimizes for latency and correctness
- Easier to insert data quality checks on the batch side
- The big pain is double the code

Kappa Architecture
- JUST use streaming, not both
- Less complex, good latency
- Can be painful when you need to read a lot of history
	- because you need to read things sequentially from Kafka
- Iceberg is making this architecture more viable

Flink UDFs
- UDFs generally won't perform as well as build-in functions
- Python UDFs are going to be even less performant since Flink isn't native Python

Flink Windows
- Data-driven windows
	- these work by staying open until you see n number of events
	- ex. count
- Time-driven windows
	- tumbling, sliding, session

Count Window
- window stays open until N number of events occur
- you can "key" on something like user, so that you have a count window "per user" for example
	- similar to `PARTITION BY` in a SQL window function
- can specify a timeout since not everyone will finish the funnel
- useful for funnels that have a predictable number of events
	- ex. a notifications funnel might be "generated, sent, delivered, opened, downstream action", etc

Tumbling Window
- fixed size, no overlap
	- for example 1:00 - 2:00, 2:00 - 3:00
- similar to hourly data
- great for chunking data

Sliding Window
- fixed size, but they can be overlapping
	- for example 1:00 - 2:00, 1:30 - 2:30
- good for finding "peak use" windows
- also can be good for handling "across midnight" issues in batch
	- for example, if a user starts a session 2 minutes before midnight and ends 2 minutes after, do they count as a DAU for both days?

Session Windows
- variable length, based on activity
- used to determine "normal" activity

Allowed Lateness vs. Watermarking (for late arriving events)
- Watermarks
	- ideal for a couple seconds late
	- defines when the computational window will execute
	- helps define ordering of events that arrive out-of-order
- Allow Lateness
	- ideal for data that is minutes late
	- usually set to 0
	- allows for reprocessing of events that fall within the late window
	- caution: can lead to funky behaviour because it may reopen and reprocess windows that have already be flushed

