# PyLmany

PyLmany is a many-to-many protocol proxy framework for Python. (and also a tasty russian dumpling)

### Basic Uasage
All you have to do is instanciate a protocol 'Client' instance and give that instance to a protocol 'Server' instance.

```
from Clients.UDPClient import UDPClient
from Servers.TCPServer import TCPServer

client = UDPClient('8.8.8.8', 53)
server = TCPServer(client)
```

You can also create a custom instance of Client and Server in order to get the change to manipulate the data before its sent/returned.
All you have to do is inherit the Client/Server class and override the ```before_send(data)``` or ```before_respond(data)``` methods and return a modified data object:

```
from Clients.HTTPClient import HTTPClient, HTTPRequest
from Server.UDPServer import UDPServer

class MyHTTPClient(HTTPClient):
    def before_send(req):
        """ :type data HTTPRequest """
        req.add_header('some-header': 'some-value')
        req.body = req.body
        return req

class MyTCPServer(TCPServer):
    def before_respond(data):
        """ :type data str """
        return data.upper()

client = MyHTTPClient('www.example.com', 80)
server = MyTCPServer(client)

```

### Hacking
You can even implement your own network protocols in PyLmany, all you need to do is to iherit from the ```AbstractClient``` or ```AbstractServer``` class and implement two abstract methods, the ```initialize``` method which needs to instanciate a socket object and save it in ```self.socket``` and a ```protocol_send(data, sock)``` method to tell PyLmany how the data should be sent to the server via the socket. an example ```ICMPClient``` class could be something like:

```
from Clients.AbstractClient import AbstractClient
from socket import *


class ICMPClient(AbstractClient):

    def initialize(self, forward_addr, forward_port):
        self.socket = socket(AF_INET, SOCK_RAW, getprotobyname('icmp'))

    def protocol_send(self, data, sock):
        """ :type sock socket"""
        sock.sendto(data, (self.forward_addr, sock.proto))

```
You can also override the ```on_receive(sock)``` method in order to implement your own protocol serialization logic.

Simple, elegant, effective.



License
----
MIT