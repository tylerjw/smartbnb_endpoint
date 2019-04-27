# smartbnb_endpoint
Endpoint server for [smartbnb webhooks](http://help.smartbnb.io/integrations-and-developers/webhooks-for-airbnb-and-homeaway).

## Dependencies
1. python3
1. [flask](http://flask.pocoo.org/docs/1.0/)


## Run
```$ python3 server.py```

## API
* This is the url you enter in the smarbnb settings page:

```http://<server_url>:9004/smartbnb```

* Get all the entries for a given listing:

```http GET http://<server_url>:9004/listing/<listing_id>```

* Get the entries for today (future endpoint for setting door lock codes):

```http GET http://<server_url>:9004/today/<listing_id>```

* Get the entry for a specific day/time:

```http GET http://weaveringrally2.duckdns.org:9004/code/22718956/2019_04_27_09_10```
