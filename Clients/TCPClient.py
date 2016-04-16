from AbstractClient import AbstractClient
from socket import *


class TCPClient(AbstractClient):

    def protocol_send(self, data, sock):
        sock.send(data)

    def initialize(self, forward_addr, forward_port):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((forward_addr, forward_port))
        self.socket = sock

