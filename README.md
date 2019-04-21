# smartbnb_endpoint
Endpoint server for [smartbnb webhooks](http://help.smartbnb.io/integrations-and-developers/webhooks-for-airbnb-and-homeaway).

## Dependencies
1. python3
1. [flask](http://flask.pocoo.org/docs/1.0/)
1. [dataset](https://dataset.readthedocs.io/en/latest/api.html)


## Run
```$ python3 server.py```

## API
1. This is the url you enter in the smarbnb settings page:
```http://<server_url>:9004/smartbnb```

1. Get all the entries for a given listing:
```http GET http://<server_url>:9004/listing/<listing_id>```

1. Get the entries for today:
```http GET http://<server_url>:9004/today/<listing_id>```
