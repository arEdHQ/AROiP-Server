import socket
from Request import HTTPRequest
import threading


class Server:

    def __init__(self, host='localhost', port=5005):
        self.host = host
        self.port = port
        self.connections = []

    def handle_single_connection(self, conn):

        try:
            data = conn.recv(1024)
        except socket.error:
            conn.close()
            self.connections.remove(conn)
            return

        request = HTTPRequest(data)
        response = ""

        if request.method == "viewer":
            response = self.handle_viewer(conn)
        elif request.method == "presenter":
            response = self.handle_presenter(conn)

        return response.encode('utf8')

    def start(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(100)

        print("Listening at", s.getsockname())

        try:
            while True:
                conn, addr = s.accept()
                print("Connected by", addr)
                self.connections.append(conn)
                t = threading.Thread(  # we start a thread for each new client
                    target=self.handle_single_connection, args=([conn]), daemon=True)
                t.start()

        except KeyboardInterrupt:
            s.close()  # On pressing ctrl + c, we close all connections
            for conn in self.connections:
                conn.close()
            quit()  # Then we shut down the server

    def handle_viewer(self, conn):
        try:
            data = conn.recv(1024)
        except socket.error:
            conn.close()
            try:
                self.connections.remove(conn)
            except ValueError:
                print("Viewer Socket Error, Value Error")

            return "Socket Error, Closing Connection\n"
        except KeyboardInterrupt:
            return "Closing Server\n"

        conn.close()
        try:
            self.connections.remove(conn)
        except ValueError:
            print("Viewer Quit, Value Error")
        return ""

    def handle_presenter(self, conn):
        while True:
            try:
                data = conn.recv(1024)
            except socket.error:
                conn.close()
                try:
                    self.connections.remove(conn)
                except ValueError:
                    print("Presenter Socket Error, Value Error")

                return "Socket Error, Closing Connection\n"
            except KeyboardInterrupt:
                return "Closing Server\n"

            response = data.decode('utf8').split("\n")[-2] + "\n"
            print(response)

            if response == "quit\n":
                conn.close()
                try:
                    self.connections.remove(conn)
                except ValueError:
                    # connection has already being removed
                    print("Presenter Quit, Value Error")

                return "Disconnected Successfully"

            for con in self.connections:
                con.sendall(response.encode('utf8'))
