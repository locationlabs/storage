# Spatial Storage Client

0.1

Python client library for interacting with [Location Labs][1] [spatial storage][2].

[1]: http://location-labs.com
[2]: http://storage.location-labs.com

Spatial storage is a RESTful service for storing and querying spatially
tagged content.


## Installation

easy install ...


## Getting Started

1. Request developer credentials.

Spatial storage uses [OAuth][1] credentials to authorize API usage. Developers
need credentials for themselves and each storage layer. Request access [here][2].

[1]: http://oauth.net
[2]: http://storage.location-labs.com/support

2. Initialize a client.

Construct a storage client using your credentials:

   from locationlabs.storage import client

   developer = client.Developer('oauth_consumer_key',
                                'oauth_consumer_secret')

   layer = client.Layer('oauth_token',
                        'oauth_token_secret')

   cli = client.Client('https://storage.location-labs.com/api/v1/content',
                       developer,
                       layer)

3. Use the client to create, query, or modify content:

For example:

   circle = client.Circle(-122.290082,37.84166,5000)
   print "\n".join(map(str,cli.search(circle)))


## Documentation

More information about the spatial storage service and API are hosted [here][1].

[1]: http://storage.location-labs.com/docs

## License

This client library is distributed under the [Apache 2.0 license][1].

[1]: http://www.apache.org/licenses/LICENSE-2.0.html

## Contributors

- [Jesse Myers](https://github.com/jessemyers)
- [Mohit Gupta](https://github.com/m0hit)
