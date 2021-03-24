class HTTPRequest:

    def __init__(self, data):
        self.method = None
        self.uri = None
        self.http_version = '1.1'  # default to HTTP/1.1 if request doesn't provide a version
        self.parse(data)

    def parse(self, data):
        lines = data.split(b'\r\n')
        print(lines)
        request_line = lines[0]
        self.method = request_line.decode()  # call decode to convert bytes to string
