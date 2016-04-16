import Clients.HTTPClient
import httplib
from Servers.AbstractServer import *
import BaseHTTPServer


class HTTPServer(AbstractServer):

    def __init__(self, client, listen_addr='', listen_port=8080, auto_start=True):
        self.httpd = BaseHTTPServer.HTTPServer((listen_addr, listen_port), self.make_request_handler)
        super(HTTPServer, self).__init__(client, listen_addr, listen_port, auto_start)

    class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

        def __init__(self, http_server, *args):
            self.http_server = http_server  # type: HTTPServer
            BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args)

        def do_handle(self):
            content_length = int(self.headers.getheader('content-length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else ''
            self.http_server.active_connection = self
            if isinstance(self.http_server.client, Clients.HTTPClient.HTTPClient):
                self.http_server.forward(Clients.HTTPClient.HTTPRequest(self.command, self.path, body, self.headers.dict))
            else:
                self.http_server.forward(body)

        def do_GET(self): self.do_handle()
        def do_POST(self): self.do_handle()
        def do_PUT(self): self.do_handle()
        def do_DELETE(self): self.do_handle()
        def do_TRACE(self): self.do_handle()
        def do_PATCH(self): self.do_handle()

        def log_message(self, format, *args):
            pass

    def make_request_handler(self, *args):
        return self.RequestHandler(self, *args)

    def initialize(self, client, listen_addr, listen_port):
        self.socket = self.httpd.socket

    def protocol_respond(self, data, conn):
        """ :type conn BaseHTTPServer.BaseHTTPRequestHandler """
        if isinstance(data, httplib.HTTPResponse):
            conn.send_response(int(data.status))
            for header, value in data.getheaders():
                if not header.lower() == 'content-length':
                    conn.send_header(header, value)
            body = data.read()
            conn.send_header('content-length', len(body))
            conn.end_headers()
            conn.wfile.write(body)
        elif isinstance(data, basestring):
            conn.send_response(200)
            conn.send_header('content-length', len(data))
            conn.end_headers()
            conn.wfile.write(data)

    def on_receive(self, sock):
        self.httpd._handle_request_noblock()