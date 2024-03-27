from util.request import Request
from util.constants import to_bytes
import re

class Router:
    def __init__(self):
        self.routes: tuple[str, re.Pattern, str] = []

    def add_route(self, http_method: str, path: str, func):
        # re_path = re.compile(r'{}'.format(path))
        re_path = re.compile(path)
        self.routes.append((http_method, re_path, func))
        # self.routes[path] = {http_method: func}

    def route_request(self, request: Request):
        for i in self.routes:
            i[1].match(request.path)
        self.routes.get(request.path)

def server_root(request):
    file_contents = fetch_file('./public/index.html')
    num_visits = str(int(request.cookies.get('visits', 0)) + 1)
    file_contents = file_contents.replace(b'{{visits}}', num_visits.encode())
    params = {'Set-Cookie': f'visits={num_visits}; Max-Age=42069'}
    # Note: may need to add all cookies in params
    return success_response('text/html', len(file_contents), params, file_contents)

def server_favicon(request):
    file_contents = fetch_file('./public/favicon.ico')
    return success_response('image/x-icon', len(file_contents), None, file_contents)

def server_image(request):
    img_path = ''
    path_split = request.path.split('/')
    for i in range(len(path_split)):
        if path_split[i] == 'images':
            for j in range(i, len(path_split)):
                img_path += j
    file_contents = fetch_file('./public/image/' + img_path)
    img_type = request.path.split('.')[:-1]
    content_types = {
        'jpg': 'image/jpeg', 'png': 'image/png', 'jpeg': 'image/jpeg'
        }
    return success_response(content_types[img_type], 
                            len(file_contents), None, file_contents)

def server_file(request):
    file_type = request.path.split('.')[:-1]
    content_types = {'html': 'text/html; charset=utf-8', 'jpg': 'image/jpeg',
                    'js': 'text/javascript', 'css': 'text/css', 
                    'ico': 'image/x-icon'}
    file_contents = b''
    try:
        file_contents = fetch_file(request.path)
    except FileNotFoundError:
        try:
            file_contents = fetch_file('.' + request.path)
        except:
            file_contents = fetch_file('./public' + request.path)
    return success_response(content_types[file_type], len(file_contents),
                             None, file_contents)

def fetch_file(path) -> tuple[int, str]:
    # sys.stdout.flush()
    with open(path, 'rb') as fi:
        file_contents = fi.read()
        return file_contents

def success_response(type, length, params: dict[str, str], content):
    response = f'HTTP/1.1 200 OK \r\n Content-Type: {type}\r\n'
    response += f'Content-Length: {length}\r\nX-Content-Type-Options: nosniff\r\n'
    if params is not None:
        for key, value in params.items():
            response += f'{key}: {value}\r\n'
    response += '\r\n'
    response = response.encode()
    response += to_bytes(content)
    return response
