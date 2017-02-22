"""Provides URLFetchConnection for appengine access."""

import time
import warnings
import base64
try:
    from google.appengine.api import urlfetch
    from google.appengine.api import urlfetch_errors
    URLFETCH_AVAILABLE = True
except ImportError:
    URLFETCH_AVAILABLE = False

from elasticsearch import Connection
from elasticsearch.exceptions import ConnectionError, ImproperlyConfigured, ConnectionTimeout, SSLError
from elasticsearch.compat import urlencode, string_types

class URLFetchConnection(Connection):
    """
    Connection using AppEngine `urlfetch` library.

    :arg http_auth: optional http auth information as either ':' separated
        string or a tuple. Any value will be passed into requests as `auth`.
    :arg use_ssl: use ssl for the connection if `True`
    :arg verify_certs: whether to verify SSL certificates
    :arg ca_certs: optional path to CA bundle. By default standard requests'
        bundle will be used.
    :arg client_cert: path to the file containing the private key and the
        certificate, or cert only if using client_key
    :arg client_key: path to the file containing the private key if using
        separate cert and key files (client_cert will contain only the cert)
    :arg headers: any custom http headers to be add to requests
    """
    def __init__(self, host='localhost', port=9200, http_auth=None,
        use_ssl=False, verify_certs=True, ca_certs=None, client_cert=None,
        client_key=None, headers=None, **kwargs):
        if not URLFETCH_AVAILABLE:
            raise ImproperlyConfigured("Please install appengine SDK to use URLFetchConnection.")

        super(URLFetchConnection, self).__init__(host=host, port=port, **kwargs)

        self.headers = headers.copy() if headers else dict()

        if http_auth is not None:
            if isinstance(http_auth, (tuple, list)):
                http_auth = tuple(http_auth)
            elif isinstance(http_auth, string_types):
                http_auth = tuple(http_auth.split(':', 1))

            self.headers['Authorization'] = "Basic %s" % base64.b64encode("%s:%s" % http_auth)

        self.base_url = 'http%s://%s:%d%s' % (
            's' if use_ssl else '',
            host, port, self.url_prefix
        )
        self.verify_certs = verify_certs

        assert not ca_certs, "ca_certs not supported by URLFetchConnection."
        assert not client_key, "client_key not supported by URLFetchConnection."
        assert not client_cert, "client_cert not supported by URLFetchConnection."

        if use_ssl and not verify_certs:
            warnings.warn(
                'Connecting to %s using SSL with verify_certs=False is insecure.' % self.base_url)

    def perform_request(self, method, url, params=None, body=None, timeout=None, ignore=()):
        url = self.base_url + url
        if params:
            url = '%s?%s' % (url, urlencode(params or {}))

        start = time.time()
        headers = self.headers.copy()
        try:

            response = urlfetch.Fetch(url,
                payload=body,
                method=method,
                headers=headers,
                allow_truncated=False,
                follow_redirects=True,
                deadline=timeout,
                validate_certificate=self.verify_certs)

            duration = time.time() - start
            raw_data = response.content
        except Exception as e:
            self.log_request_fail(method, url, url, body, time.time() - start, exception=e)
            if isinstance(e, urlfetch_errors.SSLCertificateError):
                raise SSLError('N/A', str(e), e)
            if isinstance(e, urlfetch_errors.DeadlineExceededError):
                raise ConnectionTimeout('TIMEOUT', str(e), e)
            raise ConnectionError('N/A', str(e), e)

        # raise errors based on http status codes, let the client handle those if needed
        if not (200 <= response.status_code < 300) and response.status_code not in ignore:
            self.log_request_fail(method, url, url, body, duration)
            self._raise_error(response.status_code, raw_data)

        self.log_request_success(method, url, url, body, response.status_code, raw_data, duration)

        return response.status_code, response.headers, raw_data

    def close(self):
        """
        Explicitly closes connections
        """
        pass
