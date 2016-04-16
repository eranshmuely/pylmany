from AbstractServer import AbstractServer
from socket import *


class UDPServer(AbstractServer):

    def protocol_respond(self, data, conn):
        sock, addr = conn
        sock.sendto(data, addr)

    def initialize(self, client, listen_addr, listen_port):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind((listen_addr, listen_port))
        self.socket = sock
