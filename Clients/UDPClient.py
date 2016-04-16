from AbstractClient import AbstractClient
from socket import *


class UDPClient(AbstractClient):

    def initialize(self, forward_addr, forward_port):
        sock = socket(AF_INET, SOCK_DGRAM)
        self.socket = sock

    def protocol_send(self, data, sock):
        sock.sendto(data, (self.forward_addr, self.forward_port))