# Geocoding HTTP Service
This repository contains a simple implementation of a RESTful HTTP API which provides a geocoding service using multiple geocoding service providers (Here and Google) in the backend.

# Usage
## First Time
Before using the server, you must acquire API keys for both backend services. Once the credentials are acquired, they should be stored in `geocoding/handlers.py`

```
HERE_APP_ID = "YOUR_APP_ID"
HERE_APP_CODE = "YOUR_APP_CODE"
GOOGLE_APP_ID = "YOUR_APP_KEY"
```
### Google
You can start here to get credentials: https://developers.google.com/maps/documentation/geocoding/start
### Here
You can start here to get credentials: https://developer.here.com/documentation/geocoder/topics/quick-start.html

## Starting the server
To start the server invoke the following command from the root of this repository:

`./server`

By default the server is bound to the wildcard network address (bound to all adapters) and listening on port 8888.

This can be modified by changing the server script:
```
BIND_ADDRESS = ''
BIND_PORT = 8888
```

# Geocoding Clients
There's also a standalone test client for both services, which can be invoked as follows
## Google
`./google_geocode API_KEY "Search Query"`
## Here
`./here_geocode API_ID APP_CODE "Search Query"`

# Future Improvements
* Endpoint routing should use regular expressions
* Print statements could be implemented as system log messages
* API could support a JSON format for carrying error messages
* Unit tests should be written to test implementation
