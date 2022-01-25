"""
Constants and functions related to BADSEC API endpoints.
"""

from collections import namedtuple

BADSEC_BASE_URL = 'http://127.0.0.1:8888'

BadSecApiEndPoints = namedtuple(
    'BadSecApiEndPoints',
    [
        'AUTHENTICATION',
        'USERS',
    ]
)

endpoints = BadSecApiEndPoints(
    '/auth',
    '/users',
)

def full_url_from_endpoint(endpoint):
    return "{0}{1}".format(BADSEC_BASE_URL, endpoint)

