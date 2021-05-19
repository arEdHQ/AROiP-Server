import socket
from Request import HTTPRequest
import threading


class Server:
    
    def __init__(self, host='localhost', port=5005):
        self.host = host
        self.port = port
        self.connections = []

    def handle_single_connection(self, conn):        
        data, addr = self.s.recvfrom(1024)

        request = HTTPRequest(data)
        response = ""

        if request.method == "viewer":
            response = self.handle_viewer(conn)
        elif request.method == "presenter":
            response = self.handle_presenter(conn)

        return response.encode('utf8')

    def start(self):

        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.s.bind((self.host, self.port))

        print("Listening at", self.s.getsockname())

        # t = threading.Thread(target=self.handle_request, args=([]), daemon=True)
        # t.start()

        try:
            self.handle_request()
                

        except KeyboardInterrupt:
            quit()  # Then we shut down the server

    def handle_request(self):
        oldData = b'0'
        while True:
            data, addr = self.s.recvfrom(1024)
            response = data.decode('utf8')
            print(response)

            if(response) == "init":
                print("Connected by", addr)
                self.connections.append(addr)
                self.s.sendto(oldData,addr)
            

            elif response == "quit\n":
                try:
                    self.connections.remove(addr)
                except ValueError: # connection has already being removed
                    print("Presenter Quit, Value Error")
                return "Disconnected Successfully"
            
            elif response.split()[0] == "presenter":
                oldData = response.split()[1].encode('utf8')
                for _addr in self.connections:
                    self.s.sendto(response.split()[1].encode('utf8'),_addr)
            
            else:
                self.s.sendto(oldData,addr)
