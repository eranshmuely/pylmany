from abc import *
from socket import *
from Servers.AbstractServer import *


class AbstractClient:

    __metaclass__ = ABCMeta

    def __init__(self, forward_addr, forward_port):
        self.__server = None  # type: AbstractServer
        self.forward_addr = forward_addr
        self.forward_port = forward_port
        self.socket = None # type: socket
        self.initialize(forward_addr, forward_port)
        self.buffer_size = 65536
        self.server_client_addr = None
        assert self.socket is not None, "initialize() function did not set the socket"

    def attach(self, server):
        server.watch_socket_io(self.socket, self)

    def detach(self):
        self.server.unwatch_socket_io(self.socket)

    @property
    def server(self): return self.__server

    @server.setter
    def server(self, server):
        self.__server = server
        self.attach(server)

    @server.deleter
    def server(self):
        self.detach()
        self.__server = None

    @abstractmethod
    def initialize(self, forward_addr, forward_port):
        """
        This method should initialize the client instance in terms of configuration
        at the end of the initlialize() function the client socket MUST be set like so:
        self.socket = some_socket
        """

    def before_send(self, data):
        """
        this method gives the user a chance to manipulate the data before it gets sent to its destination
        """
        return data

    def send(self, data):
        """
        This method sends the data to its destination, calls an abstract method called protocol_send
        which must implement the data send itself
        """
        data = self.before_send(data)
        self.protocol_send(data, self.socket)
        self.server.poll()

    @abstractmethod
    def protocol_send(self, data, sock):
        """
        This method MUST implement the protocol send logic
        :param sock: the socket to send on
        :type sock socket
        :param data: data to send
        """

    def on_receive(self, sock):
        """
        This method should implement what to do whenever socket IO occurs, default is to make server respond the data
        to whomever contacted it
        :param sock: socket object that has IO
        :type sock socket
        """
        data, addr = sock.recvfrom(self.buffer_size)
        if not data:
            self.server.unwatch_socket_io(sock)
        self.server.respond(data)