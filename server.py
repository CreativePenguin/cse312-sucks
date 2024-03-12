import socketserver
import sys
from util.request import Request
from pymongo import MongoClient
from util.chat import chat_message, chat_history, delete_chat
from util.auth import login, register
from util.constants import num_bytes, ERROR_RESPONSE, HOME_PATH, \
    SUCCESS_RESPONSE, DEFAULT_200_RESPONSE
from util.constants import to_str, to_bytes
import re


class MyTCPHandler(socketserver.BaseRequestHandler):

    client = MongoClient('mongo')
    # client = MongoClient('localhost')

    db = client['cse312']

    def handle(self):
        received_data = self.request.recv(2048)
        request = Request(received_data)

        path = request.path.strip()
        # increment num_visits
        if path == '/visit-counter':
            num_visits = str(int(request.cookies.get('visits', 0)) + 1)
            response = SUCCESS_RESPONSE.format(
                type='text/html',
                len=len(num_visits)
            )
            self.request.sendall(f'{response}\r\n\
Set-Cookie: visits={num_visits}; Max-Age=42069\r\n\r\n{num_visits}'.encode())
            return
        if path[-11:] == 'favicon.ico':
            response = process_favicon(SUCCESS_RESPONSE)
            self.request.sendall(response)
            return

        if path == '/chat-messages':
            if request.method == 'GET':
                response = chat_history(self.db)
                self.request.sendall(response)
                return
            if request.method == 'POST':
                chat_message(request, self.db)
            self.request.sendall(DEFAULT_200_RESPONSE)
            return

        if path == '/chat-history':
            response = chat_history(self.db)
            self.request.sendall(response)
            return

        if path == '/register':
            response = register(request, self.db)
            # redirect
            path = '/index.html'

        if path == '/login':
            response = login(request, self.db)
            # redirect
            path = '/index.html'
            if response != None:
                path, contents = fetch_file(path, HOME_PATH, request)
                self.request.sendall(response + contents)
                self.request.sendall(f'{response}\r\n Set-Cookie: visits={num_visits}; Max-Age=42069\r\n\r\n{contents}'.encode())
                return
            else:
                path = '/error.html'
                self.request.sendall(ERROR_RESPONSE.encode())
                return

        # if path[:14] == '/chat-messages':
        #     print('CHAT-MESSAGE CALLED')
        #     print(request)
        #     if request.method == 'DELETE':
        #         response = delete_chat(request, self.db)
        #         self.request.sendall(response)
        #         return

        if path == '/' or path == 'public/index.html':
            path, contents = fetch_file('public/index.html', HOME_PATH, request)
            num_visits = str(int(request.cookies.get('visits', 0)) + 1)
            contents = contents.replace(b'{{visits}}', num_visits.encode())
            length = len(contents)
            response = SUCCESS_RESPONSE.format(type='text/html; charset=utf-8', len=length)
            response += f'\r\nSet-Cookie: visits={num_visits}; Max-Age=42069\r\n\r\n'
            response = to_bytes(response) + to_bytes(contents)
            self.request.sendall(response)
            return
        
        path, contents = fetch_file(path, HOME_PATH, request)
        print(path)
        if path == None:
            print('path is none')
            response = ERROR_RESPONSE
            try:
                self.request.sendall(response.encode('utf-8'))
            except AttributeError:
                self.request.sendall(response)
            return
        file_type = path.split('.')[-1].lower()
        content_types = {'html': 'text/html; charset=utf-8', 'jpg': 'image/jpeg',
                        'js': 'text/javascript', 'css': 'text/css', 'ico': None}
        # print(contents.replace(b'{{visits}}', b'3'))
        # print('random statement after printing path')
        content_type = content_types.get(file_type, '')
        # TODO: Parse the HTTP request and use self.request.sendall(response) to send your response
        # self.request.sendall(
        # 'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 5\r\n\r\nhello'.encode()
        # )
        file_bytes = num_bytes(path)
        if file_bytes == None:
            response = ERROR_RESPONSE
        response = f'{SUCCESS_RESPONSE.format(type=content_type, len=num_bytes(path))}'
        # response = f'{SUCCESS_RESPONSE.format(type=content_type, len=len(contents))}'
        self.request.sendall(response.encode('utf-8') + contents)
        # self.request.sendall(f'{response.encode()}\r\n\r\n{contents}')


def fetch_file(path, home_path, request) -> tuple[str, bytes]:
    if path == '':
        return (None, None)
    if path == '/':
        path = 'public/index.html'
    file_contents = b''
    num_visits = 0
    try:
        # sys.stdout.flush()
        with open(path, 'rb') as fi:
            file_contents = fi.read()
            num_visits = str(int(request.cookies.get('visits', 0)) + 1)
            file_contents = file_contents.replace(b'{{visits}}', num_visits.encode())
    except FileNotFoundError:
        print('file not found')
        if path[0] == '/':
            path = path[1:]
        try:
            with open(path, 'rb') as fi:
                # file_contents = fi.read()
                # num_visits = str(int(request.cookies.get('visits', 0)) + 1)
                # file_contents = file_contents.replace(b'{{visits}}', num_visits.encode())
                file_contents = fi.read()
        except FileNotFoundError:
            print('doubly not found file')
            return (None, None)
    except IsADirectoryError:
        path = home_path + path + 'index.html'
        with open(path, 'rb') as fi:
            return (path, fi.read())
    # cookie = f'Set-Cookie: visits={num_visits}; Max-Age=42069'
    # file_contents = cookie.encode() + b'\r\n\r\n' + file_contents
    file_contents = b'\r\n\r\n' + file_contents
    return (path, file_contents)

def process_favicon(success_response):
    filename = './public/favicon.ico'
    response = success_response.format(type='image/x-icon', 
                                       len=num_bytes(filename))
    content = ''
    with open(filename, 'rb') as fi:
        content = fi.read()
    return to_bytes(response) + '\r\n\r\n'.encode() + content

def main():
    host = "0.0.0.0"
    port = 8080

    socketserver.TCPServer.allow_reuse_address = True

    server = socketserver.TCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))
    sys.stdout.flush()
    sys.stderr.flush()

    server.serve_forever()


if __name__ == "__main__":
    main()
