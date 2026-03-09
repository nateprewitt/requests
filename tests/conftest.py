try:
    from http.server import HTTPServer, SimpleHTTPRequestHandler
except ImportError:
    from BaseHTTPServer import HTTPServer
    from SimpleHTTPServer import SimpleHTTPRequestHandler

import ssl
import threading
from collections.abc import Generator

import pytest

from requests.compat import urljoin


def prepare_url(value):
    # Issue #1483: Make sure the URL always has a trailing slash
    httpbin_url = value.url.rstrip("/") + "/"

    def inner(*suffix):
        return urljoin(httpbin_url, "/".join(suffix))

    return inner


@pytest.fixture
def httpbin(httpbin):
    return prepare_url(httpbin)


@pytest.fixture
def httpbin_secure(httpbin_secure):
    return prepare_url(httpbin_secure)


def _make_trustme_server(
    tmp_path_factory: pytest.TempPathFactory,
    *identities: str,
    **issue_cert_kwargs: str,
) -> Generator[tuple[str, int, str]]:
    """Yield ``(host, port, ca_bundle_path)`` for a local HTTPS server."""
    # delay importing until the fixture in order to make it possible
    # to deselect the test via command-line when trustme is not available
    import trustme

    tmpdir = tmp_path_factory.mktemp("certs")
    ca = trustme.CA()
    server_cert = ca.issue_cert(*identities, **issue_cert_kwargs)
    ca_bundle = str(tmpdir / "ca.pem")
    ca.cert_pem.write_to_path(ca_bundle)

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    server_cert.configure_cert(context)
    server = HTTPServer(("localhost", 0), SimpleHTTPRequestHandler)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()

    yield "localhost", server.server_address[1], ca_bundle

    server.shutdown()
    server_thread.join()


@pytest.fixture
def trustme_server(
    tmp_path_factory: pytest.TempPathFactory,
) -> Generator[tuple[str, int, str]]:
    """A local HTTPS server with a proper SAN cert signed by trustme."""
    yield from _make_trustme_server(tmp_path_factory, "localhost")


@pytest.fixture
def nosan_server(
    tmp_path_factory: pytest.TempPathFactory,
) -> Generator[tuple[str, int, str]]:
    """A local HTTPS server serving a cert from trustme without a SAN field."""
    yield from _make_trustme_server(tmp_path_factory, common_name="localhost")
