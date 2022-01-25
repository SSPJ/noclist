import requests

from requests.exceptions import RequestException
from hashlib import sha256
from time import sleep
from typing import List

from . import urls


class Session():
    """
    Creates and maintains a stateful session with the BADSEC server.
    """

    MAX_TRIES = 3

    def __init__(self):
        self.session = requests.Session()
        self.token = None

    def __enter__(self):
        """ Allow usage as a context manager. """
        return self

    def _calculate_checksum(self, endpoint) -> str:
        """ Return the hexidecimal hash of the auth token and endpoint. """
        return sha256(bytes(self.token + endpoint, encoding='utf8')).hexdigest() 

    def _client(self, method, endpoint, headers=None, backoff=0.5):
        """ Generic method for contacting the API, with backoff and retry. """
        tries = range(self.MAX_TRIES)
        last = tries[-1]
        url = urls.full_url_from_endpoint(endpoint)
        client = getattr(self.session, method)
        for t in tries:
            try:
                response = client(url, headers=headers, timeout=10)
                response.raise_for_status()
            except RequestException as ex:
                if t == last: raise
                sleep(backoff * 2 ** t)
            else:
                return response
        return None

    def _get_auth_token(self):
        """ Obtain the auth token. """
        try:
            auth = self._client('head', urls.endpoints.AUTHENTICATION)
            assert 'Badsec-Authentication-Token' in auth.headers 
        except (RequestException, AssertionError) as ex:
            raise RequestException("Unable to authenticate") from ex
        else:
            return auth.headers['Badsec-Authentication-Token']

    def auth(self):
        """ Obtain and set the auth token needed for future API calls. """
        self.token = self._get_auth_token()

    def users(self) -> List[str]:
        """ Obtain a list of users. """
        if not self.token:
            self.auth()
        try:
            checksum = self._calculate_checksum(urls.endpoints.USERS)
            headers = {'X-Request-Checksum': checksum}
            response = self._client('get', urls.endpoints.USERS, headers)
        except RequestException as ex:
            # there is a chance that the request failed due to the server
            # restarting and invalidating the previous token, so we clear
            # this variable -- TODO: check response for 500 status
            self.token = None
            raise RequestException("Unable to retreive list of users") from ex
        else:
            # the server might also return CRLF endings, but this seems
            # to work with the test server
            return response.text.split('\n') if len(response.text) > 0 else []

    def __exit__(self, exc_type, exc_value, traceback):
        """ Close the session when the context manager exits. """
        self.session.close()

