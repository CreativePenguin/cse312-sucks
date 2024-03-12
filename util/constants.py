HOME_PATH = './public/'
ERROR_RESPONSE = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\
Content-Length: 36\r\nX-Content-Type-Options: nosniff\
\r\n\r\nThe requested content does not exist'
SUCCESS_RESPONSE =  'HTTP/1.1 200 OK\r\nContent-Type: {type}\r\nContent-Length:\
{len}\r\nX-Content-Type-Options: nosniff'
DEFAULT_200_RESPONSE = b'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\
Content-Length:7\r\nX-Content-Type-Options: nosniff\r\nsuccess\r\n\r\n'


def num_bytes(filename):
    file_length = 0
    try:
        with open(filename, 'rb') as (fi):
            file_length = len(fi.read())
    except FileNotFoundError:
        return 0
    return file_length

def printCollection(dbCollection):
    for i in dbCollection.find({}):
        print(i)

def to_bytes(str_or_bytes) -> bytes:
    if type(str_or_bytes) == str:
        return str_or_bytes.encode()
    if type(str_or_bytes) == bytes or type(str_or_bytes) == bytearray:
        return str_or_bytes
    return None

def to_str(str_or_bytes) -> str:
    if type(str_or_bytes) == str:
        return str_or_bytes
    if type(str_or_bytes) == bytes or type(str_or_bytes) == bytearray:
        return str_or_bytes.decode()
    return None

def success_response(type, length, content, additional_fields):
    SUCCESS_RESPONSE.format(type=type, length=length)
