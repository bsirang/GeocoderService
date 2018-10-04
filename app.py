from http import server
import urllib.parse

BIND_ADDRESS = ''
BIND_PORT = 8888

SERVER_ADDRESS = (BIND_ADDRESS, BIND_PORT)

class HTTPGetRequestRouter:
    def __init__(self):
        self.handlers = list()

    def add_handler(self, path_pattern, handler_callable):
        if not isinstance(path_pattern, str):
            raise TypeError("First argument must be str")
        if not callable(handler_callable):
            raise TypeError("Second argument must be callable")

        print("Adding handler for path pattern %s" % path_pattern)
        self.handlers.append((path_pattern, handler_callable))

    def process_route(self, path_tokens, query_dict):
        if len(path_tokens) == 0:
            path_tokens.append('')

        for path_pattern, handler_callable in self.handlers:
            if path_tokens[0] == path_pattern:
                return handler_callable(path_tokens[1:], query_dict)

        return 404, ""

root_router = HTTPGetRequestRouter()

class GeoCodingRequestHandler(server.BaseHTTPRequestHandler):
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
    def __init__(self, name):
        self.router = HTTPGetRequestRouter()
        self.name = name

    def __call__(self, *args, **kwargs):
        path_tokens = args[0]
        query_dict = args[1]
        print("%s %s %s" % (self.name, path_tokens, query_dict))
        return self.router.process_route(path_tokens, query_dict)

class FooHandler(GenericEndpointHandler):
    def __init__(self):
        super(FooHandler, self).__init__(name="foo")
        self.router.add_handler("bar", FooHandler.bar_handler)
        self.router.add_handler("", FooHandler.root_handler)

    @classmethod
    def bar_handler(cls, path_tokens, query_dict):
        print("foo/bar/ handler %s %s" % (path_tokens, query_dict))
        return 200, """
        {"dummy": "json"}
        """

    @classmethod
    def root_handler(cls, path_tokens, query_dict):
        print("foo/ handler")
        return 200, "{}"

class GeoLocateHandler(GenericEndpointHandler):
    def __init__(self):
        super(GeoLocateHandler, self).__init__(name="geolocate")
        self.router.add_handler("google", self.google_handler)
        self.router.add_handler("here", self.here_handler)
        self.router.add_handler("", self.root_handler)

    @staticmethod
    def google_handler(path_tokens, query_dict):
        return 200, """{"service": "google"}"""

    @staticmethod
    def here_handler(path_tokens, query_dict):
        return 200, """{"service": "here"}"""

    @staticmethod
    def root_handler(path_tokens, query_dict):
        return 200, """{"service": "all"}"""

def root_handler(path_tokens, query_dict):
    print("/ handler")
    return 200, "{}"

if __name__ == "__main__":
    print("Starting Geo Coding Service...")
    print("Listning on port %d" % BIND_PORT)

    #foo_handler = FooHandler()
    geolocate_handler = GeoLocateHandler()

    root_router.add_handler('geolocate', geolocate_handler)
    root_router.add_handler('', root_handler)

    httpd = server.HTTPServer(SERVER_ADDRESS, GeoCodingRequestHandler)
    httpd.serve_forever()