from AbstractClient import AbstractClient
import Servers.HTTPServer
import httplib
import urllib


class HTTPRequest(object):

    def __init__(self, method="POST", path='/', body=None, headers={}):
        self.method = method
        self.path = path
        self.body = body
        self.headers = headers

    def add_header(self, key, value):
        self.headers.update({key: value})

    def get_header(self, key, default=None):
        return self.headers.get(key)


class HTTPClient(AbstractClient):

    def __init__(self, forward_addr, forward_port):
        self.http_conn = None  # type: httplib.HTTPConnection
        super(HTTPClient, self).__init__(forward_addr, forward_port)

    def initialize(self, forward_addr, forward_port):
        self.http_conn = httplib.HTTPConnection(forward_addr, forward_port)
        self.http_conn.connect()
        self.socket = self.http_conn.sock

    def build_request(self, method="POST", path='', body=None, headers={}):
        return HTTPRequest(method, path, body, headers)

    def send(self, data):
        if not isinstance(data, HTTPRequest):
            data = self.build_request(body=data)
        data = self.before_send(data)
        self.protocol_send(data, self.socket)
        self.server.poll()

    def on_receive(self, sock):
        try:
            response = httplib.HTTPResponse(sock)
            response.begin()
            if isinstance(self.server, Servers.HTTPServer.HTTPServer):
                self.server.respond(response)
            else:
                self.server.respond(response.read())
        except:
            pass

    def send_http_request(self, req):
        """ :type req HTTPRequest """
        if not isinstance(req, HTTPRequest):
            req = HTTPRequest(body=str(req))
        self.http_conn.request(req.method, req.path, req.body, req.headers)

    def protocol_send(self, data, sock):
        self.initialize(self.forward_addr, self.forward_port)
        self.server.watch_socket_io(self.socket, self)
        self.server.unwatch_socket_io(sock)
        self.send_http_request(data)

    def before_send(self, req):
        """ :type req HTTPRequest"""
        return req