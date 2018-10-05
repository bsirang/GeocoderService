import http.client
import json
import urllib

class HereGeocoderClient:
    """ Client for Here's geocoding API. """
    def __init__(self, app_id, app_code):
        self.app_id = app_id
        self.app_code = app_code
        self.h = http.client.HTTPSConnection("geocoder.api.here.com", 443)
        self.response = {}

    def issue_query(self, searchtext):
        searchtext = urllib.parse.quote(searchtext, safe='')
        self.response = {}
        try:
            self.h.request("GET", "/6.2/geocode.json?app_id=%s&app_code=%s&searchtext=%s" % (self.app_id, self.app_code, searchtext))
            r = self.h.getresponse()
            if r.getcode() == 200:
                self.response = json.loads(r.read())
        except:
            print("Exception during Here API request")

    def get_coordinates(self):
        coords = list()
        if 'Response' in self.response and 'View' in self.response['Response']:
            for view in self.response['Response']['View']:
                for result in view['Result']:
                    if 'Location' in result:
                        if 'DisplayPosition' in result['Location']:
                           coords.append(result['Location']['DisplayPosition'])
        return coords

class GoogleGeocoderClient:
    """ Client for Google's geocoding API """
    def __init__(self, app_id):
        self.app_id = app_id
        self.h = http.client.HTTPSConnection("maps.googleapis.com", 443)
        self.response = {}

    def issue_query(self, searchtext):
        searchtext = urllib.parse.quote(searchtext, safe='')
        self.response = {}
        try:
            self.h.request("GET", "/maps/api/geocode/json?address=%s&key=%s" % (searchtext, self.app_id))
            r = self.h.getresponse()
            if r.getcode() == 200:
                self.response = json.loads(r.read())
        except:
            print("Exception during Google API request")

    def get_coordinates(self):
        coords = list()
        if 'results' in self.response:
            for result in self.response['results']:
                if 'geometry' in result and 'location' in result['geometry']:
                    coords.append(result['geometry']['location'])
        return coords


