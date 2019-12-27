# NCCOStorage

Simple service that allows hosting [NCCOs](https://developer.nexmo.com/voice/voice-api/ncco-reference) over a period of time and basic templating.

If you want to know more on how NCCOs can be used, check out nexmo's [Voice API Overview](https://developer.nexmo.com/voice/voice-api/overview)

## Getting started

Make sure you have [pipenv](https://docs.pipenv.org/) installed.

There is a makefile with some basic tasks:

```
# runs the program
$ make run
======== Running on http://0.0.0.0:8080 ========
(Press CTRL+C to quit)

# runs the tests
$ make test
======= test session starts =======
...output omitted...
======= X passed in Y seconds ======
```

For development, just run `pipenv install --dev` and pipenv should take care of setting everything up for you!

## Examples

You can create a bucket to store NCCOs:

```
$ curl -i -X POST \
  -H 'Content-Type: application/json' \
  -d'{"id": "mybucket"}' \
  "http://localhost:8080/bucket"

HTTP/1.1 201 Created
Content-Type: application/json; charset=utf-8
Content-Length: 29
Date: Mon, 12 Mar 2018 21:53:55 GMT
Server: Python/3.6 aiohttp/3.0.7

{"id": "mybucket", "ttl": 60}
```

You can then add an NCCO to it:

```
$ curl -i -X POST \
  -H 'Content-Type: application/json' \
  -d'{"ncco": "[{\"action\": \"talk\", \"text\": \"Hello VAPI!\"}]"}' \
  "http://localhost:8080/bucket/mybucket/ncco"

HTTP/1.1 201 Created 
Content-Type: application/json; charset=utf-8
Content-Length: 114
Date: Mon, 12 Mar 2018 22:01:54 GMT
Server: Python/3.6 aiohttp/3.0.7

{"ncco_id": "14c3b5c5-9869-4c83-b10d-5a6a654e3e62", "ncco": "[{\"action\": \"talk\", \"text\": \"Hello VAPI!\"}]"}
```

And finally you can render it. You can give this URL to the VAPI, so it can correctly retrieve your NCCO.

```
$ curl -i "http://localhost:8080/bucket/mybucket/ncco/14c3b5c5-9869-4c83-b10d-5a6a654e3e62/render"

HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 43
Date: Mon, 12 Mar 2018 22:04:11 GMT
Server: Python/3.6 aiohttp/3.0.7

[{"action": "talk", "text": "Hello VAPI!"}]
```

## Templating

The service supports basic templating, so that you can dinamically set certain parameters of the NCCO. For example, you could have the talk action mention the conversation ID this NCCO will play in:

```
$ curl -i -X POST \
  -H 'Content-Type: application/json' \
  -d'{"ncco": "[{\"action\": \"talk\", \"text\": \"{{conversation_uuid}}\"}]"}' \
  "http://localhost:8080/bucket/mybucket/ncco"

HTTP/1.1 201 Created 
Content-Type: application/json; charset=utf-8

{"ncco_id": "bdbe863b-7d09-4ebb-8572-486f5448d8fe", "ncco": ...omitted...}

$ curl -i "http://localhost:8080/bucket/mybucket/ncco/bdbe863b-7d09-4ebb-8572-486f5448d8fe/render?conversation_uuid=CON-bdbe863b-7d09-4ebb-8572-486f5448d8fe"

HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 72
Date: Mon, 12 Mar 2018 22:14:07 GMT
Server: Python/3.6 aiohttp/3.0.7

[{"action": "talk", "text": "CON-bdbe863b-7d09-4ebb-8572-486f5448d8fe"}]
```

Amazing right?

## License

MIT