# smartbnb_endpoint
Endpoint server for smartbnb webhooks.  The smartbnb.io webhooks is described [here](http://help.smartbnb.io/integrations-and-developers/webhooks-for-airbnb-and-homeaway)

## Testing
1. Run server
    $ python3 server.py
1. Send sample data using [httpie](https://httpie.org/):
    $ http POST http://localhost:9004/smarbnb < sample.json
