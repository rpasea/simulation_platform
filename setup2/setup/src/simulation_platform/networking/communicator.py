import SocketServer
import threading
import socket
import traceback

PORT = 7777

def handler_factory(communicator):
    class tcp_handler(SocketServer.BaseRequestHandler):
        def __init__(self, *args, **kwargs):
            self.communicator = communicator
            SocketServer.BaseRequestHandler.__init__(self, *args, **kwargs)
        
        def setup(self):
            self.communicator.register_handler(self.client_address[0], self)
            SocketServer.BaseRequestHandler.setup(self)
        
        def handle(self):
            while True:
                try:
                    self.data = self.request.recv(1024)
                    if len(self.data) > 0:
                        self.communicator.received_data(self.client_address[0], self.data)
                    else:
                        self.communicator.close_connection(self.client_address[0])
                        break
                except Exception, e:
                    print traceback.format_exc()
                    self.communicator.close_connection(self.client_address[0])
                    break
    return tcp_handler

class ThreadedServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

def thread_func(server):
    server.serve_forever()

class communicator:
    def __init__(self, listener, port = PORT):
        self.port = port
        self.listener = listener
        self.handlers = {}
        self.sockets = {}
        self.socket_streams = {}
        self.server = None
        self.running = False
        self.thread = None
    
    def start(self):
        handler_class = handler_factory(self)
        SocketServer.TCPServer.allow_reuse_address = True
        self.server = ThreadedServer(('localhost', self.port), handler_class)
        
        self.thread = threading.Thread(target = thread_func, args = (self.server,))
        self.thread.start()
        self.running = True

    def stop(self):
        for address in self.sockets:
            self.sockets[address].shutdown(socket.SHUT_RDWR)
            self.sockets[address].close()
        self.server.shutdown()
        self.thread.join()
        self.server.socket.close()
        self.running = False

    def register_handler(self, address, handler):
        if address not in self.sockets:
            self.handlers[address] = handler
            self.sockets[address] = handler.request

    def connect(self, address, port):
        if address not in self.sockets:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect((address, port))
                self.sockets[address] = sock
                self.server.process_request(sock, (address, port))
            except Exception, e:
                print traceback.format_exc()
                sock.close()

    def close_connection(self, address):
        self.sockets[address].close()
        del self.sockets[address]

    def send(self, address, data):
        if address in self.sockets:
            socket = self.sockets[address]
            self.sockets[address].sendall(data)
    
    def received_data(self, address, data):
        self.listener.received_data(address, data)
