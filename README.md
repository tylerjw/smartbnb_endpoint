# smartbnb_endpoint
Endpoint server for [smartbnb webhooks](http://help.smartbnb.io/integrations-and-developers/webhooks-for-airbnb-and-homeaway).

## Dependencies
1. python3
1. [flask](http://flask.pocoo.org/docs/1.0/)
1. [dataset](https://dataset.readthedocs.io/en/latest/api.html)


## Run
```$ python3 server.py```

## API
* This is the url you enter in the smarbnb settings page:

```http://<server_url>:9004/smartbnb```

* Get all the entries for a given listing:

```http GET http://<server_url>:9004/listing/<listing_id>```

* Get the entries for today (future endpoint for setting door lock codes):

```http GET http://<server_url>:9004/today/<listing_id>```
