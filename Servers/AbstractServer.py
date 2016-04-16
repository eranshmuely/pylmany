from abc import *
from socket import *
from select import select
import time
from Clients.AbstractClient import AbstractClient


class AbstractServer:

    __metaclass__ = ABCMeta

    def __init__(self, client, listen_addr='0.0.0.0', listen_port=8080, auto_start=True):
        """
        :param client: The client that the server should use to forward information
        :type client AbstractClient
        :param listen_addr: Host that the server should listen on, default = 0.0.0.0
        :param listen_port: Port that the server should listen on, default = 8080
        :param auto_serve: Should the server be started immediately
        """
        self.listen_addr = listen_addr
        self.listen_port = listen_port
        self.socket_input_list = []  # type: list[socket]
        self.socket = None  # type: socket
        self.main_loop_active = True
        self.buffer_size = 65536
        self.delay = 0.0001
        self.socket_delegates = {}
        self.active_connection = None  # type: (socket, address)
        self.initialize(client, listen_addr, listen_port)
        assert self.socket is not None, "initialize() function did not instantiate socket"
        self.active_connection = (self.socket, (listen_addr, listen_port))

        self.client = client
        self.client.server = self
        assert self.client.socket is not None, "client socket not instantiated"

        self.initialize_main_loop()
        if auto_start:
            self.start_main_loop()


    @abstractmethod
    def initialize(self, client, listen_addr, listen_port):
        """
        This method should initialize the server instance in terms of configuration, but NOT start the server
        at the end, of the initlialize() function the socket MUST be instantiated like so:
        self.socket = some_socket
        """

    def watch_socket_io(self, sock, delegate):
        """
        This method tells the server to watch a socket for IO, adds a delegate instance. whenever IO occurs,
        the delegate's on_receive(sock) method will be called with a reference to the socket
        """
        self.socket_input_list.append(sock)
        self.socket_delegates.update({sock: delegate})

    def unwatch_socket_io(self, sock):
        """
        This method un-watches a socket
        """
        try:
            self.socket_delegates.pop(sock)
            self.socket_input_list.remove(sock)
            sock.close()
        except:
            pass

    def break_main_loop(self):
        self.main_loop_active = False

    def resume_main_loop(self):
        self.main_loop_active = True

    def initialize_main_loop(self):
        if isinstance(self.socket, socket): self.watch_socket_io(self.socket, self)

    def start_main_loop(self):
        while True:
            time.sleep(self.delay)
            if self.main_loop_active:
                self.poll()

    def poll(self):
        try:
            r_list, o_list, e_list = select(self.socket_input_list, [], [])
        except error:
            print "other side probably closed the connection"
            exit()

        for sock in r_list:
            delegate = self.socket_delegates.get(sock)
            assert delegate is not None, "socket {} has no delegate".format(sock)
            assert hasattr(delegate, 'on_receive'), "delegate class {} does not have an 'on_recieve' method"\
                .format(delegate.__class__.__name__)
            delegate.on_receive(sock)
            break

    def on_receive(self, sock):
        """
        This method should implement what to do whenever socket IO occurs, default is to forward to client
        :param sock: socket object that raised IO
        :type sock socket
        """
        data, addr = sock.recvfrom(self.buffer_size)
        if not data:
            self.unwatch_socket_io(sock)
        else:
            self.active_connection = (sock, addr)
            self.forward(data)

    def forward(self, data):
        """
        This method calls before_forward(data) to give user a chance to manipulate the data before the client sends it
        them, it calls the client's send(data) method so that the client will send the data to the destination
        :param addr: address of the client who initiated the connection
        :param data: data received from socket
        """
        self.client.send(data)

    def before_forward(self, data):
        return data

    def respond(self, data):
        """
        This method tells the server to respond to whomever contacted it. this method should be called by the client
        This method calls the server's before_respond(data) method to give the user a change to mutate it and then
        calls the abstract protocol_send(data) method to send the data back to whomever contacted it
        :param data: the data that the client wants the server to respond to whomever contacted it
        :param sock: the client socket that made the connection on the other side, used to choose the responding socket
        """
        data = self.before_respond(data)
        self.protocol_respond(data, self.active_connection)

    @abstractmethod
    def protocol_respond(self, data, conn):
        """
        This method MUST implement the protocol in which the data should be responded
        :param conn a tuple containing the appropriate socket as well as the client address and port
        :type conn tuple(socket, client AF_INET addr)
        """

    def before_respond(self, data):
        return data

