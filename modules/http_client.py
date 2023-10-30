"""
Auxiliary module to perform HTTP requests
and parse the result.
"""
try:
    import httplib
except ImportError:
    import http.client as httplib

import sys
import ssl
import re
import json
import time
from modules import logger as logger_factory

# Some constants
URL_PARSER_REGEX = r'^(http[s]?)://([a-z|A-Z|.|-]+)(:[0-9]{3,5})?(/[^\n ]*$)'
url_parser = re.compile(URL_PARSER_REGEX)
logger = logger_factory.create_logger()


def __parse_url(url):
    """
    Parses the http schema, hostname, port and resource
    for a given URL.

    Args:
        url (str): URL to parse
    Returns:
        tuple (str): A tuple indicating the HTTP schema,
            hostname, port and resource to consume.
    Raises:
        ValueError: If it is not possible to parse the required
            element from the given URL.
    """
    result = url_parser.findall(url)
    if not result:
        msg = (
            'Unable to parse the given URL: %s - Regex used: %s'
            % (url, URL_PARSER_REGEX)
        )
        raise ValueError(msg)
    
    components = result[0]
    schema, hostname, port, resource =  components
    port = port.replace(":", "", 1)

    # Some encodings for the resource
    resource = resource.replace("#", "%23")

    return (schema, hostname, port, resource)

def http_request(
        url, 
        method, 
        retries=2, 
        timeout=60,
        headers={}, 
        data={}, 
        cert_file=None, 
        key_file=None,
        raise_on_failure=True
    ):
    """
    Consumes a resource using the HTTP protocol and parses its result.

    Args:
        url (str): Resource URL.
        method (str): HTTP request method, e.g: GET, POST, PUT.
        retries (int): In case of failures, how many times the request
            is going to be retried.
        timeout (int): HTTP request timeout, in seconds.
        headers (dict[str, str]): HTTP request headers.
        data (dict | str): HTTP request data, if required.
        cert_file (str): Path to the certificate used in SSL authentication
            This is optional.
        cert_file (str): Path to the key file used in SSL authentication
            This is optional.
        raise_on_failure (bool): Determines if an exception is raised
            if there is a failure consuming the HTTP resource.
    
    Returns:
        dict | bytes: HTTP response content.
    
    Raises:
        ValueError: If there are issues parsing the URL or the data
            for performing the HTTP request. Also, if they are issues
            parsing the response data.
        RuntimeError: Error consuming the resource from the server.
    """
    MAX_ATTEMPTS_TO_DICT = 5
    default_headers = {
        'Accept': 'application/json'
    }
    req_headers = default_headers if not headers else headers
    json_response = req_headers.get('Accept', '') == 'application/json'
    http_schema, hostname, port, resource = __parse_url(url)
    is_https = http_schema == 'https'

    # Parse HTTP request data
    req_data = None if not data else data
    if req_data:
        if isinstance(req_data, dict):
            req_headers["Content-Type"] = "application/json"
            req_data = json.dumps(req_data)
        if not isinstance(req_data, str):
            error_msg = (
                "Please encode your request data as 'str'. "
                "Also make sure to provide the appropiate headers"
            )
            raise ValueError(error_msg)
        
    # Parse the port properly
    if port:
        port = port.replace(":", "", 1)
        port = int(port)
    else:
        port = 443 if is_https else 80

    # Build the connection params
    connection_params = {
        "host": hostname,
        "port": port,
        "timeout": timeout,
    }
    if cert_file and key_file:
        connection_params["cert_file"] = cert_file
        connection_params["key_file"] = key_file
    
    # Perform the request.
    last_attempt_exception = None
    for _ in range(retries):
        try:
            # Create the connection
            if is_https:
                conn = httplib.HTTPSConnection(**connection_params)
            else:
                conn = httplib.HTTPConnection(**connection_params)

            # Consume the resource
            conn.request(method, resource, req_data, req_headers)
            response = conn.getresponse()
            status, res = response.status, response.read()
            conn.close()

            if status == 200:
                if json_response:
                    res_as_dict = res.decode("utf-8")

                    # Parse as a Python object
                    for _ in range(MAX_ATTEMPTS_TO_DICT):
                        res_as_dict = json.loads(res_as_dict)
                        if isinstance(res_as_dict, dict):
                            break
                    if not isinstance(res_as_dict, dict):
                        error_msg = (
                            "Unable to parse the response as a dict after %d attempts"
                            % (MAX_ATTEMPTS_TO_DICT)
                        )
                        raise ValueError(error_msg)

                    return res_as_dict
                else:
                    logger.warning("Returning response as bytes")
                    return res

            # Invalid code
            logger.error('Invalid status code:\n Status: %s, \n Response: %s', status, res)
            time.sleep(1)
        except Exception as e:
            last_attempt_exception = e
            logger.error('Error performing HTTP request to: %s', url)
            logger.error('Description: %s', e)
            if is_https and not connection_params.get("context"):
                logger.warning('Disabling server certificate validation')
                no_cert_validation = ssl._create_unverified_context()
                no_cert_validation.set_ciphers('DEFAULT')
                connection_params["context"] = no_cert_validation

                if isinstance(last_attempt_exception, ssl.SSLError):
                    # Reset the exception.
                    last_attempt_exception = None

    # Unable to retrieve the requested resource
    error_msg = (
        "Unable to consume the HTTP resource: %s \n"
        "Method: %s \n" 
        % (url, method)
    )
    logger.error(error_msg)
    if not raise_on_failure:
        return None
    if (
        last_attempt_exception 
        and isinstance(last_attempt_exception, Exception)
    ):
        logger.critical(
            "Exception chained - Type: %s - Message: %s",
            type(last_attempt_exception),
            last_attempt_exception,
        )

    raise RuntimeError(error_msg)
