import pytest
import responses
import requests

from .. import api
from .. import urls

class TestBadSecAPI:

    # TODO: abstract common code into fixtures
    # also TODO: patch time.sleep to speed up test execution

    class TestAuth:

        @responses.activate
        def test_should_call_authentication_endpoint(self):
            url = urls.full_url_from_endpoint(urls.endpoints.AUTHENTICATION)
            headers = {'Badsec-Authentication-Token': "9D11C948-ED41-277F-C5F6-C76FFCE7CD86"}
            responses.add(responses.HEAD, url, headers=headers, status=200)

            session = api.Session()
            session.auth()

            assert responses.assert_call_count(url, 1) is True

        @responses.activate
        def test_should_retry_authentication_endpoint_if_connection_drops(self):
            url = urls.full_url_from_endpoint(urls.endpoints.AUTHENTICATION)
            headers = {'Badsec-Authentication-Token': "9D11C948-ED41-277F-C5F6-C76FFCE7CD86"}
            responses.add(responses.HEAD, url, body=requests.exceptions.Timeout())
            responses.add(responses.HEAD, url, body=requests.exceptions.Timeout())
            responses.add(responses.HEAD, url, headers=headers, status=200)

            session = api.Session()
            session.auth()

            assert responses.assert_call_count(url, 3) is True

        @responses.activate
        def test_should_retry_authentication_endpoint_if_bad_status(self):
            url = urls.full_url_from_endpoint(urls.endpoints.AUTHENTICATION)
            headers = {'Badsec-Authentication-Token': "9D11C948-ED41-277F-C5F6-C76FFCE7CD86"}
            responses.add(responses.HEAD, url, headers=headers, status=404)
            responses.add(responses.HEAD, url, headers=headers, status=503)
            responses.add(responses.HEAD, url, headers=headers, status=200)

            session = api.Session()
            session.auth()

            assert responses.assert_call_count(url, 3) is True

        @responses.activate
        def test_should_not_retry_more_than_three_times(self):
            url = urls.full_url_from_endpoint(urls.endpoints.AUTHENTICATION)
            headers = {'Badsec-Authentication-Token': "9D11C948-ED41-277F-C5F6-C76FFCE7CD86"}
            responses.add(responses.HEAD, url, headers=headers, status=404)
            responses.add(responses.HEAD, url, headers=headers, status=503)
            responses.add(responses.HEAD, url, headers=headers, status=500)
            responses.add(responses.HEAD, url, headers=headers, status=200)

            session = api.Session()
            with pytest.raises(requests.exceptions.RequestException):
                session.auth()

            assert responses.assert_call_count(url, 3) is True

        @responses.activate
        def test_should_raise_exception_if_token_header_is_missing(self):
            url = urls.full_url_from_endpoint(urls.endpoints.AUTHENTICATION)
            responses.add(responses.HEAD, url, status=200)

            session = api.Session()
            with pytest.raises(requests.exceptions.RequestException):
                session.auth()

    class TestUsers:

        @responses.activate
        def test_should_call_user_endpoint_with_auth_header(self):
            auth_url = urls.full_url_from_endpoint(urls.endpoints.AUTHENTICATION)
            headers = {'Badsec-Authentication-Token': "9D11C948-ED41-277F-C5F6-C76FFCE7CD86"}
            responses.add(responses.HEAD, auth_url, headers=headers, status=200)
            url = urls.full_url_from_endpoint(urls.endpoints.USERS)
            responses.add(
                responses.GET,
                url,
                body="123456789\n987654321",
                status=200,
                match=[
                    responses.matchers.header_matcher({
                        'X-Request-Checksum': "899a05a9440ad7f0c1b5f6cfb3cb1025d4db3fc954bf6a4cf8db8db3a43ca3d4"
                    })
                ]
            )

            session = api.Session()
            actual = session.users()
            expected = ["123456789", "987654321"]

            assert responses.assert_call_count(url, 1) is True
            assert actual == expected

        @responses.activate
        def test_should_not_call_authenticate_multiple_times(self):
            auth_url = urls.full_url_from_endpoint(urls.endpoints.AUTHENTICATION)
            headers = {'Badsec-Authentication-Token': "9D11C948-ED41-277F-C5F6-C76FFCE7CD86"}
            responses.add(responses.HEAD, auth_url, headers=headers, status=200)
            url = urls.full_url_from_endpoint(urls.endpoints.USERS)
            responses.add(responses.GET, url, status=200)

            session = api.Session()
            session.users()
            session.users()

            assert responses.assert_call_count(auth_url, 1) is True

        @responses.activate
        def test_should_retry_users_endpoint_if_connection_drops(self):
            auth_url = urls.full_url_from_endpoint(urls.endpoints.AUTHENTICATION)
            headers = {'Badsec-Authentication-Token': "9D11C948-ED41-277F-C5F6-C76FFCE7CD86"}
            responses.add(responses.HEAD, auth_url, headers=headers, status=200)
            url = urls.full_url_from_endpoint(urls.endpoints.USERS)
            responses.add(responses.GET, url, body=requests.exceptions.Timeout())
            responses.add(responses.GET, url, body=requests.exceptions.Timeout())
            responses.add(responses.GET, url, status=200)

            session = api.Session()
            session.users()

            assert responses.assert_call_count(url, 3) is True

        @responses.activate
        def test_should_retry_users_endpoint_if_bad_status(self):
            auth_url = urls.full_url_from_endpoint(urls.endpoints.AUTHENTICATION)
            headers = {'Badsec-Authentication-Token': "9D11C948-ED41-277F-C5F6-C76FFCE7CD86"}
            responses.add(responses.HEAD, auth_url, headers=headers, status=200)
            url = urls.full_url_from_endpoint(urls.endpoints.USERS)
            responses.add(responses.GET, url, status=404)
            responses.add(responses.GET, url, status=503)
            responses.add(responses.GET, url, status=200)

            session = api.Session()
            session.users()

            assert responses.assert_call_count(url, 3) is True

        @responses.activate
        def test_should_not_retry_more_than_three_times(self):
            auth_url = urls.full_url_from_endpoint(urls.endpoints.AUTHENTICATION)
            headers = {'Badsec-Authentication-Token': "9D11C948-ED41-277F-C5F6-C76FFCE7CD86"}
            responses.add(responses.HEAD, auth_url, headers=headers, status=200)
            url = urls.full_url_from_endpoint(urls.endpoints.USERS)
            responses.add(responses.GET, url, status=404)
            responses.add(responses.GET, url, status=503)
            responses.add(responses.GET, url, status=500)
            responses.add(responses.GET, url, status=200)

            session = api.Session()
            with pytest.raises(requests.exceptions.RequestException):
                session.users()

            assert responses.assert_call_count(url, 3) is True


    def test_calculate_checksum(self):
        """ Small unit test. Independently checked with `echo -n "12345/users" | sha256sum` """
        session = api.Session()
        session.token = "12345"
        actual = session._calculate_checksum("/users")
        expected = "c20acb14a3d3339b9e92daebb173e41379f9f2fad4aa6a6326a696bd90c67419"
        assert actual == expected

