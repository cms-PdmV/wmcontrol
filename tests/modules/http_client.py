"""
This module checks that 'modules/http_client.py' works
properly.
"""
import unittest
from modules import http_client, logger as logger_factory


class BaseTest(unittest.TestCase):
    """
    Sets up different scenarios to test
    the HTTP client.
    """

    def setUp(self):
        """
        Prepare the test scenarios.
        """
        self.logger = logger_factory.create_logger()
        self.valid_public_url = (
            "https://cms-pdmv-prod.web.cern.ch"
            "/mcm/public/restapi/requests/get_dict/B2G-RunIISummer20UL17NanoAODv9-03570"
        )
        self.invalid_by_redirection = (
            "https://cms-pdmv.cern.ch"
            "/mcm/public/restapi/requests/get_dict/B2G-RunIISummer20UL17NanoAODv9-03570"
        )
        self.invalid_by_auth = (
            "https://cms-pdmv-prod.web.cern.ch"
            "/mcm/restapi/requests/get/B2G-RunIISummer20UL17NanoAODv9-03570"
        )
        self.invalid_url_pattern = (
            "ws://cms-pdmv-prod.web.cern.ch"
            "/mcm/public/restapi/requests/get_dict/B2G-RunIISummer20UL17NanoAODv9-03570"
        )
        self.http_url = 'http://info.cern.ch/hypertext/WWW/TheProject.html'
        self.headers_for_bytes_response = {
            'Content-type': 'application/json'
        }
        self.headers_for_plain_response = {
            'Content-type': 'text/html'
        }
    
    def test_public_resource(self):
        """
        Consume a public resource that doesn't require any kind
        of authentication.
        """
        response = http_client.http_request(url=self.valid_public_url, method="GET")
        expected_requestor = "pdmvserv"
        expected_group = "ppd"
        self.assertIsInstance(
            response, 
            dict, 
            "The response content has not the type required"
        )
        self.assertEqual(
            expected_requestor, 
            response.get("Requestor", ""), 
            "The 'Requestor' field doesn't match"
        )
        self.assertEqual(
            expected_group, 
            response.get("Group", ""), 
            "The 'Group' field doesn't match"
        )


    def test_server_issues(self):
        """
        Consume a HTTP endpoint that doesn't
        return a HTTP 200 response and raises issues.
        """
        def __consume_resource():
            """
            The client raises a RuntimeError due to
            a HTTP 301 response that ask the user to
            consume the resource from the new domain.
            """
            _ = http_client.http_request(url=self.invalid_by_redirection, method="GET")
        
        self.assertRaises(RuntimeError, __consume_resource)

    
    def test_authentication_issues(self):
        """
        Consume a HTTP endpoint that doesn't
        return a HTTP 200 response and raises issues
        related to authentication.
        """
        def __consume_resource():
            """
            The client raises a RuntimeError due to
            a HTTP 302 response that sends the user
            to the CERN SSO login page.
            """
            _ = http_client.http_request(url=self.invalid_by_auth, method="GET")
        
        self.assertRaises(RuntimeError, __consume_resource)


    def test_invalid_url(self):
        """
        Attempts to consume a HTTP resource with an invalid URL.
        """
        def __consume_resource():
            """
            The client raises a ValueError due to
            the URL is invalid.
            """
            _ = http_client.http_request(url=self.invalid_url_pattern, method="GET")
        
        self.assertRaises(ValueError, __consume_resource)

    
    def test_bytes_return(self):
        """
        Consume a HTTP resource and checks that the returned
        data is a 'bytes' value.
        """
        response = http_client.http_request(
            url=self.valid_public_url, 
            method="GET",
            headers=self.headers_for_bytes_response
        )
        self.assertIsInstance(
            response, 
            bytes, 
            "The response content has not the type required"
        )

    
    def test_http_request(self):
        """
        Check that it is possible to consume HTTP
        pages, without TLS.
        """
        response = http_client.http_request(
            url=self.http_url, 
            method="GET",
            headers=self.headers_for_plain_response
        )
        response_str = response.decode("utf-8")
        self.assertIsInstance(response, bytes, "The response content has not the type required")
        self.assertIn("The World Wide Web project", response_str)

