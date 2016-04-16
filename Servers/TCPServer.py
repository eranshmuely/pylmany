from AbstractServer import AbstractServer
from socket import *


class TCPServer(AbstractServer):

    def initialize(self, client, listen_addr, listen_port):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind((listen_addr, listen_port))
        sock.listen(500)
        self.socket = sock

    def on_receive(self, sock):
        """ :type sock socket """
        if sock == self.socket:
            conn, addr = sock.accept()
            self.active_connection = (conn, addr)
            self.watch_socket_io(conn, self)
        else:
            super(TCPServer, self).on_receive(sock)

    def protocol_respond(self, data, conn):
        sock, addr = conn
        sock.send(data)
