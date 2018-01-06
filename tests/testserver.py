import pytest
import threading
import requests

from tests.testserver.server import Server, consume_socket_content

def response_handler(sock):
    req = consume_socket_content(sock, timeout=0.5)
    sock.send(
        b'HTTP/1.1 302 FOUND\r\n'
        b'Content-Length: 0\r\n'
        b'Location: /get#relevant-section\r\n\r\n'
    )
    redir_req = consume_socket_content(sock, timeout=0.5)
    sock.send(
        b'HTTP/1.1 200 OK\r\n\r\n'
    )

close_server = threading.Event()
server = Server(response_handler, wait_to_close_event=close_server)

with server as (host, port):
    print(host, port)
    while True:
        pass
