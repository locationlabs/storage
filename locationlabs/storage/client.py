# Copyright 2010 Location Labs
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oauth import oauth
import urllib
import urlparse
import httplib
import json

class HttpError(Exception):
    '''Utility for interrupting requests in response to HTTP errors'''
    def __init__(self,status,reason,url,method):
        self.status = status
        self.reason = reason
        self.url = url
        self.method = method
        
    def __str__(self):
        return "%s %s (%s %s)" % (self.status,self.reason,self.method,self.url)

class ObjectEncoder(json.JSONEncoder):
    '''Utility for JSON encoding objects using their dictionaries'''
    def default(self, obj):
        if isinstance(obj, object):
            # omit json keys for empty values
            return dict([(k,v) for (k,v) in obj.__dict__.iteritems() if v])
        return json.JSONEncoder.default(self, obj)

class Developer(oauth.OAuthConsumer):
    '''Developer access to the Spatial Storage platform is through OAuth.
    Each developer has a unique oauth_consumer_key and oauth_consumer_secret pair.'''
    def __init__(self,
                 oauth_consumer_key,
                 oauth_consumer_secret):
        oauth.OAuthConsumer.__init__(self,
                                     oauth_consumer_key,
                                     oauth_consumer_secret)

class Layer(oauth.OAuthToken):
    '''Developers store content within one or more layers.
    Each layer has a unique oauth_token and oauth_token_secret pair.'''
    def __init__(self,
                 oauth_token,
                 oauth_token_secret):
        oauth.OAuthToken.__init__(self,
                                  oauth_token,
                                  oauth_token_secret)


class Content:
    '''Developer content must supply a longitude, latitude, and a unique id.
    Content may also provide an optional label, timestamp, and flat key-value
    property map.'''
    def __init__(self,id,lon,lat,label=None,time=None,properties=dict()):
        self.id = id
        self.lon = lon
        self.lat = lat
        self.label = label
        self.time = time
        self.properties = properties;

    def __str__(self):
        return json.dumps(self,cls=ObjectEncoder)

class Properties:
    '''Content properties may be updated after content creation.'''
    def __init__(self,properties=dict()):
        self.properties = properties

    def __str__(self):
        return json.dumps(self,cls=ObjectEncoder)

class Circle:
    '''Content queries (spatial searches) are currently limited to circle queries'''
    def __init__(self,lon,lat,radius):
        self.lon = lon
        self.lat = lat
        self.radius = radius

    def to_query_string(self):
        # create a query string
        return "&".join(["%s=%s" % (k,v) for (k,v) in self.__dict__.iteritems()])

    def __str__(self):
        return "within %s meters of (%f,%f)" % (self.radius,self.lat,self.lon)

class Client:
    '''Client interface for Spatial Storage'''
    def __init__(self,url,developer,layer):
        self.url = url
        self.developer = developer
        self.layer = layer

    def _make_http_connection(self,http_url):
        parsed_url = urlparse.urlparse(http_url)

        if parsed_url.scheme == 'https':
            return httplib.HTTPSConnection(parsed_url.netloc)
        else:
            return httplib.HTTPConnection(parsed_url.netloc)

    def _make_request(self,http_url,http_method,http_headers=None,body=None,parameters=None):
        '''Issue an API request'''

        # prepare an OAuth signature
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.developer,
                                                                   self.layer,
                                                                   http_method=http_method,
                                                                   http_url=http_url,
                                                                   parameters=parameters)

        oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),
                                   self.developer,
                                   self.layer)

        # open an HTTP connection
        connection = self._make_http_connection(http_url)

        headers = oauth_request.to_header()
 	if http_headers:
            headers.update(http_headers)

        # issue request, passing OAuth signature as Authorization header
        connection.request(http_method,
                           http_url,
                           headers=headers,
                           body=body)

        # read response
        response = connection.getresponse()
        if response.status != 200:
            raise HttpError(response.status, response.reason, http_url, http_method)

        return response.read()

    def create(self,content):
        '''Create new content, either one at a time or in a batch.'''
        http_url = self.url
        http_headers={
            "Accept":"application/json", 
            "Content-Type":"application/json"
            }

        if hasattr(content, '__iter__'):
            body = json.dumps(content,cls=ObjectEncoder)
        else:
            body = json.dumps([content],cls=ObjectEncoder)
        self._make_request(http_url,'POST', http_headers=http_headers, body=content)

    def search(self,circle):
        '''Search for content within a bounding circle.'''
        parameters = circle.__dict__
        http_url = self.url + "?" + circle.to_query_string()
	http_headers={
            "Content-Type":"application/json"
            }
        body = self._make_request(http_url,'GET',http_headers=http_headers,parameters=parameters)
        return [Content(**dct) for dct in json.loads(body)]

    def delete(self,id):
        '''Delete content by id.'''
        http_url = "/".join([self.url,urllib.quote(id)])
        self._make_request(http_url,'DELETE')

    def get(self,id):
        '''Get content by id.'''
        http_url = "/".join([self.url,urllib.quote(id)])
        http_headers={
            "Content-Type":"application/json"
            }
	body = self._make_request(http_url,'GET',http_headers=http_headers)
        return Content(**json.loads(body))
    
    def update(self,id,properties):
        '''Get content by id.'''
        http_url = "/".join([self.url,urllib.quote(id)])
        http_headers={
            "Accept":"application/json", 
            "Content-Type":"application/json"
            }
	body = json.dumps(properties,cls=ObjectEncoder)
        self._make_request(http_url,'PUT',http_headers=http_headers,body=body)

