from util.constants import to_str
class Request:

    def __init__(self, request: bytes):
        self.method = ""
        self.path = ""
        self.http_version = ""

        if request is not None:
            self.headers: dict[str, str] = {}
            self.body: bytes = b''
            self.cookies: dict[str, str] = {}
            self.orig_request = request
            self.body_length = 0
            self.missing_bytes = 0

            try:
                request_head, self.body = request.split(b'\r\n\r\n', 1)
            except ValueError:
                request_head = request.strip()
                print("hey bobby, look it's a request with no body!", request)
            requestsli = request_head.decode().split('\r\n')
            first_line = requestsli[0].strip()
            first_line_iter = iter(first_line.split(' '))
            try:
                self.method = next(first_line_iter).strip()
                self.path = next(first_line_iter).strip()
                self.http_version = next(first_line_iter).strip()
            except StopIteration:
                pass
            # try:
            #     self.path = first_line.split(' ')[1].strip()
            # except IndexError:
            #     print('INDEX ERROR', 'AAAAAAAAAA', first_line)
            # self.method = first_line.split(' ')[0].strip()
            # self.http_version = first_line.split(' ')[2].strip()
            for i in requestsli[1:]:
                key, value = i.split(':', 1)
                self.headers[key.strip()] = value.strip()
                if key.strip() == 'Content-Length':
                    self.body_length = int(value.strip())
            self.missing_bytes = self.body_length - len(self.body)
            if not self.headers.get('Cookie', None) == None:
                cookieli = self.headers['Cookie'].split(';')
                cookieli = self.headers.get('Cookie').split(';')
                if cookieli == None:
                    self.cookies = None
                for i in cookieli:
                    key, value = i.split('=', 1)
                    self.cookies[key.strip()] = value.strip()

    def __str__(self):
        return to_str(self.orig_request)


def test1():
    request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n')
    assert request.method == "GET"
    assert "Host" in request.headers
    assert request.headers["Host"] == "localhost:8080"  # note: The leading space in the header value must be removed
    assert request.body == b""  # There is no body for this request.
    # When parsing POST requests, the body must be in bytes, not str

    # This is the start of a simple way (ie. no external libraries) to test your code.
    # It's recommended that you complete this test and add others, including at least one
    # test using a POST request. Also, ensure that the types of all values are correct


if __name__ == '__main__':
    test1()
