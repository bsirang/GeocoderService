import geocoding.clients
import http.server
import json
import urllib.parse

# You must obtain the various IDs and Keys from Here and Google
# and populate the variables below with the appropriate values.
# Here: https://developer.here.com/documentation/geocoder/topics/quick-start.html
# Google: https://developers.google.com/maps/documentation/geocoding/start

HERE_APP_ID   = "PASTE HERE"
HERE_APP_CODE = "PASTE HERE"
GOOGLE_APP_ID = "PASTE HERE"

class HTTPGetRequestRouter:
    """
    Route an HTTP GET request to the appropriate handler.

    Maintains a list of handlers and invokes them based on the requested endpoint.
    """
    def __init__(self):
        self.handlers = list()

    def add_handler(self, path_pattern, handler_callable):
        """ Add a handler for a given path."""
        if not isinstance(path_pattern, str):
            raise TypeError("First argument must be str")
        if not callable(handler_callable):
            raise TypeError("Second argument must be callable")

        self.handlers.append((path_pattern, handler_callable))

    def process_route(self, path_tokens, query_dict):
        """ Invoke the appropriate handler based on the given path. """
        if len(path_tokens) == 0:
            path_tokens.append('')

        for path_pattern, handler_callable in self.handlers:
            if path_tokens[0] == path_pattern: # TODO regexp
                return handler_callable(path_tokens[1:], query_dict)

        return 404, ""

class GeoCodingRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    Entry point for HTTP GET requests.

    This class inherits from http.server.BaseHTTPRequestHandler and is the
    class that should be passed in when instantiating an http.server.HTTPServer object.
    """
    @staticmethod
    def get_decomposed_path_string(path_string):
        query_tokens = path_string.split('?')
        if len(query_tokens) == 2: #was there a query string?
            query_string = query_tokens[-1]
            path_string = query_tokens[0]
        else:
            query_string = ''
        path_tokens = path_string.split('/')
        return path_tokens, urllib.parse.parse_qs(query_string)

    def do_GET(self):
        print("GET %s" % self.path)
        path_tokens, query_dict = self.get_decomposed_path_string(self.path)
        print("query = %s" % query_dict)
        print("path = %s" % path_tokens)

        status_code, response_message = root_router.process_route(path_tokens[1:], query_dict)

        self.send_response(status_code)
        self.send_header('content-type', 'application/json')
        self.end_headers()
        self.wfile.write(bytearray(response_message, 'utf-8'))


class GenericEndpointHandler():
    """
    Generic functionality for handling an endpoint.

    Inherit from this class and add handlers to handle endpoints.
    Children of this class can be used to register handlers for endpoints recursively.
    In other words, a handler for foo can be added that itself adds handlers for bar and baz.
    These then can then be invoked if the client requests /foo/bar and /foo/baz respectively.
    """
    def __init__(self, name):
        self.router = HTTPGetRequestRouter()
        self.name = name

    def __call__(self, *args, **kwargs):
        path_tokens = args[0]
        query_dict = args[1]
        print("%s %s %s" % (self.name, path_tokens, query_dict))
        return self.router.process_route(path_tokens, query_dict)

    def get_name(self):
        return self.name

class GeoCodeHandler(GenericEndpointHandler):
    """
    Endpoint handler for /geocode/xxx endpoints.

    Three handlers are procided
    /geocode/ - Attempts to use here geocoding API with Google fallback
    /geocode/here - Attempts to use here geocoding API
    /geocode/google - Attempts to use Google geocoding API
    """
    def __init__(self):
        super(GeoCodeHandler, self).__init__(name="geocode")
        self.router.add_handler("google", self.google_handler)
        self.router.add_handler("here", self.here_handler)
        self.router.add_handler("", self.root_handler)

    @staticmethod
    def format_coordinates(coords):
        if 'lat' in coords:
            coords['Latitude'] = coords['lat']
            del coords['lat']
        if 'lng' in coords:
            coords['Longitude'] = coords['lng']
            del coords['lng']

        return coords

    @staticmethod
    def google_handler(path_tokens, query_dict):
        result = {
            "location": {}
        }
        if not 'searchtext' in query_dict:
            return 422, """{}"""
        client = geocoding.clients.GoogleGeocoderClient(GOOGLE_APP_ID)
        client.issue_query(query_dict["searchtext"][0])
        coords = client.get_coordinates()
        if len(coords) > 0:
            result["location"] = GeoCodeHandler.format_coordinates(coords[0])
        return 200, json.dumps(result)

    @staticmethod
    def here_handler(path_tokens, query_dict):
        result = {
            "location": {}
        }
        if not 'searchtext' in query_dict:
            return 422, """{}"""
        client = geocoding.clients.HereGeocoderClient(HERE_APP_ID, HERE_APP_CODE)
        client.issue_query(query_dict["searchtext"][0])
        coords = client.get_coordinates()
        if len(coords) > 0:
            result["location"] = GeoCodeHandler.format_coordinates(coords[0])
        return 200, json.dumps(result)

    @staticmethod
    def root_handler(path_tokens, query_dict):
        result = {
            "location": {}
        }
        if not 'searchtext' in query_dict:
            return 422, """{}"""
        client = geocoding.clients.HereGeocoderClient(HERE_APP_ID, HERE_APP_CODE)
        client.issue_query(query_dict["searchtext"][0])
        coords = client.get_coordinates()
        if len(coords) > 0:
            result["location"] = GeoCodeHandler.format_coordinates(coords[0])
            return 200, json.dumps(result)

        # If we made it here, we should fall back to Google
        print("Attempting fallback to Google services")
        client = geocoding.clients.GoogleGeocoderClient(GOOGLE_APP_ID)
        client.issue_query(query_dict["searchtext"][0])
        coords = client.get_coordinates()
        if len(coords) > 0:
            result["location"] = GeoCodeHandler.format_coordinates(coords[0])
        return 200, json.dumps(result)


def root_handler(path_tokens, query_dict):
    """ Trivial handler for root endpoint. """
    print("/ handler")
    return 200, "{}"

# Register endpoint handlers
geocode_handler = GeoCodeHandler()

root_router = HTTPGetRequestRouter()
root_router.add_handler(geocode_handler.get_name(), geocode_handler)
root_router.add_handler('', root_handler)