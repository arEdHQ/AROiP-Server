import socket
from Request import HTTPRequest
import threading
from Sync import merge, diff
import time
import json


class Server:

    def __init__(self, host='192.168.1.69', port=5005):
        self.host = host
        self.port = port
        self.connections = []
        self.viewers = []  # to be used for broadcast
        self.isUpdated = False

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
            self.viewers.append(conn)
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
        serverShadow = {}
        try:
            while(True):
                cachedServerCopy = self.serverCopy
                updates = diff(serverShadow, cachedServerCopy)

                if updates is None:
                    continue
                conn.sendall(json.dumps(updates))  # send serverUpdates here

                data = conn.recv(1024)
                response = data.decode('utf8').split("\n")[-2]

                if response == '200':
                    serverShadow = cachedServerCopy
                elif response == "quit":
                    break
                else:
                    # log the errors out here
                    # increase sleep time if viewer keeps on denying response
                    time.sleep(0.030)
                    continue
                time.sleep(0.050)

        except KeyboardInterrupt:
            return "Closing Server\n"

        conn.close()
        try:
            self.connections.remove(conn)
        except ValueError:
            print("Viewer Quit, Value Error")
        return ""

    def handle_presenter(self, conn):
        serverShadow = {}

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

            update = data.decode('utf8').split("\n")[-2] + "\n"

            if update == "quit\n":
                conn.close()
                try:
                    self.connections.remove(conn)
                except ValueError:
                    # connection has already being removed
                    print("Presenter Quit, Value Error")

                return "Disconnected Successfully"

            update = json.loads(update)

            # lock servercopy here
            presenterUpdates, serverShadow, self.serverCopy = merge(
                update, serverShadow, self.serverCopy)
            # Unlock servercopy here

            conn.sendall(json.dumps(presenterUpdates))
