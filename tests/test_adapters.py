import ssl
from unittest.mock import patch

import pytest

import requests
import requests.adapters
from requests.adapters import HTTPAdapter


def test_request_url_trims_leading_path_separators():
    """See also https://github.com/psf/requests/issues/6643."""
    a = requests.adapters.HTTPAdapter()
    p = requests.Request(method="GET", url="http://127.0.0.1:10000//v:h").prepare()
    assert "/v:h" == a.request_url(p, {})


class TestCustomSSLContext:
    """Test Requests behaviors when provided a custom SSLContext."""

    def _make_pool(self, **kwargs):
        from urllib3.connectionpool import HTTPSConnectionPool

        pool = HTTPSConnectionPool("example.com", 443)
        pool.conn_kw.update(kwargs)
        return pool

    def test_no_ssl_context_loads_certifi(self):
        adapter = HTTPAdapter()
        pool = self._make_pool()

        adapter.cert_verify(pool, "https://example.com", verify=True, cert=None)

        assert pool.cert_reqs == "CERT_REQUIRED"
        assert pool.ca_certs is not None

    def test_custom_ssl_context_skips_certifi(self):
        adapter = HTTPAdapter()
        ctx = ssl.create_default_context()
        pool = self._make_pool(ssl_context=ctx)

        adapter.cert_verify(pool, "https://example.com", verify=True, cert=None)

        assert pool.cert_reqs == "CERT_REQUIRED"
        assert not getattr(pool, "ca_certs", None)
        assert not getattr(pool, "ca_cert_dir", None)

    def test_explicit_verify_path_precedence(self):
        adapter = HTTPAdapter()
        ctx = ssl.create_default_context()
        pool = self._make_pool(ssl_context=ctx)
        ca_bundle = __file__ # Use this file as a stand-in we know exists

        # The verify path should take precedence over a custom SSLContext.
        adapter.cert_verify(pool, "https://example.com", verify=ca_bundle, cert=None)

        assert pool.cert_reqs == "CERT_REQUIRED"
        assert pool.ca_certs == ca_bundle

    def test_verify_false_ignores_ssl_context(self):
        adapter = HTTPAdapter()
        ctx = ssl.create_default_context()
        pool = self._make_pool(ssl_context=ctx)

        adapter.cert_verify(pool, "https://example.com", verify=False, cert=None)

        assert pool.cert_reqs == "CERT_NONE"

    def test_http_url_ignores_ssl_context(self):
        adapter = HTTPAdapter()
        pool = self._make_pool()

        adapter.cert_verify(pool, "http://example.com", verify=True, cert=None)

        assert pool.cert_reqs == "CERT_NONE"

    def test_custom_ssl_context_e2e(self, trustme_server):
        """Validate our custom SSLContext with a real HTTPS request."""
        host, port, ca_bundle = trustme_server
        ctx = ssl.create_default_context()
        ctx.load_verify_locations(ca_bundle)
        ca_count_before = len(ctx.get_ca_certs())

        class CustomSSLContextAdapter(HTTPAdapter):
            def init_poolmanager(self, *args, **kwargs):
                kwargs["ssl_context"] = ctx
                return super().init_poolmanager(*args, **kwargs)

        s = requests.Session()
        s.mount("https://", CustomSSLContextAdapter())

        r = s.get(f"https://{host}:{port}/", verify=True)
        assert r.status_code == 200
        # No new certs should be loaded in the SSLContext
        assert len(ctx.get_ca_certs()) == ca_count_before