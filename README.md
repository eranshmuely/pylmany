# PyLmany

PyLmany is a many-to-many protocol proxy framework for Python (and also a tasty Russian dumpling).

### Basic Usage
All you have to do is instanciate a protocol ```Client``` instance and give that instance to a protocol ```Server``` instance. Pylmany will use the ```Server``` instance to listen for incomming connections and then forward them to the desired destination using the ```Client``` instance that is tied to the server:

```
from Clients.UDPClient import UDPClient
from Servers.TCPServer import TCPServer

client = UDPClient('8.8.8.8', 53) # tell pylmany to forward data to 8.8.8.8 on UDP 53
server = TCPServer(client, listen_addr='0.0.0.0', listen_port=8080) # tell pylmany to listen on TCP port 8080
```

You can also create a custom subclass of ```Client``` or ```Server``` in order to get the chance to manipulate the data before its forwarded/returned by pylmany. In order to do so, you just need to inherit from the appropriate ```Client```/```Server``` class and then override the ```before_send(data)``` or ```before_respond(data)``` methods to return a modified instance of the data object to pylmany's processing pipeline:

```
from Clients.HTTPClient import HTTPClient, HTTPRequest
from Servers.UDPServer import UDPServer
import json

class MyHTTPClient(HTTPClient):
    def before_send(req):
        """ :type req HTTPRequest """
        req.add_header('content-type': 'application/json')
        req.method = 'PUT'
        req.body = json.dumps({'user_data': req.body.lower()})
        return req

class MyTCPServer(TCPServer):
    def before_respond(data):
        """ :type data str """
        return data.upper()

client = MyHTTPClient('www.example.com', 80)
server = MyTCPServer(client) # default listen port is 8080

```

### Hacking
You can even implement your own network protocols for pylmany. All you need to do is to iherit from the ```AbstractClient``` or ```AbstractServer``` class and implement two abstract methods: the ```initialize``` method which needs to instanciate a socket object and save it in ```self.socket``` and the ```protocol_send(data, sock)``` method to tell pylmany how the data should be sent to the destination via the socket. 
an example ```ICMPClient``` class could look a little something like:

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
You can also override the ```on_receive(sock)``` method in order to implement your own socket reading logic, it's super simple. 
take a look at the ```TCPServer``` or ```HTTPServer``` classes for example.

Simple, elegant, effective.


License
----
MIT
