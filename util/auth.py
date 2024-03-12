from urllib.parse import parse_qs
import hashlib
import random
import bcrypt
import html
from os import listdir

from util.constants import SUCCESS_RESPONSE
from util.constants import num_bytes
from util.constants import printCollection

def extract_credentials(req):
    req_iter = iter(req.body.strip().split('='))
    ret_val = {}
    next_key = next(req_iter, None)
    while True:
        value = next(req_iter, None)
        if next_key is None or value is None:
            break
        ret_val[next_key] = percent_unencoding(value.split('&')[0])
        next_key = percent_unencoding(value.split('&')[1])

def percent_unencoding(encoded_str):
    encoded_str.replace(f'%20', ' ')
    encoded_str.replace(f'%21', '!')
    encoded_str.replace(f'%22', '"')
    encoded_str.replace(f'%23', '#')
    encoded_str.replace(f'%24', '$')
    encoded_str.replace(f'%25', '%')
    encoded_str.replace(f'%26', '&')
    encoded_str.replace(f'%26', '&')
    encoded_str.replace(f'%27', "'")
    encoded_str.replace(f'%28', "(")
    encoded_str.replace(f'%29', ")")
    encoded_str.replace(f'%2A', "*")
    encoded_str.replace(f'%2B', "+")
    encoded_str.replace(f'%2C', ",")
    encoded_str.replace(f'%2F', "/")
    encoded_str.replace(f'%3A', ":")
    encoded_str.replace(f'%3B', ";")
    encoded_str.replace(f'%3D', "=")
    encoded_str.replace(f'%3F', "?")
    encoded_str.replace(f'%40', "@")
    encoded_str.replace(f'+', " ")
    return encoded_str

def validate_password(password):
    if len(password) < 8:
        return False
    specials = {'!', '@', '#', '$', '%', '^', '&', '(', ')', '-', '_', '='}
    containsUpper = False
    containsLower = False
    containsNumber = False
    containsSpecial = False
    for i in password:
        if i.isalnum():
            if i.isdigit():
                containsNumber = True
            elif i.upper() == i:
                containsUpper = True
            elif i.lower() == i:
                containsLower = True
        elif i in specials:
            containsSpecial = True
        else:
            return False
    return containsLower and containsUpper and containsNumber and containsSpecial

def register(request, db):
    users = db['users']
    request_body = parse_qs(request.body)
    if len(request_body.keys()) < 2:
        return None
    # username = request_body.get(b'username_reg', [b''])[0]
    print('register request_body', request_body)
    username = request_body[b'username_reg'][0]
    username = html.escape(username.decode()).encode()
    # password = request_body.get(b'password_reg', [b''])[0]
    password = request_body[b'password_reg'][0]
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password, salt)
    users.insert_one({'username': username, 'password': hash, 'auth': None})
    
def login(request, db):
    users = db['users']
    request_body = parse_qs(request.body)
    if len(request_body.keys()) < 2:
        return None
    print('login request_body', request)
    # username = request_body.get(b'username_reg', [b''])[0]
    username = request_body[b'username_login'][0]
    username = html.escape(username.decode()).encode()
    password = request_body[b'password_login'][0]
    # password = request_body.get(b'password_reg', [b''])[0]
    user = users.find({'username': username}, {})
    if user == None:
        return None
    is_valid = False
    for i in user:
        db_password = i['password']
        if db_password != None:
            # if bcrypt.checkpw(i['password'], password):
            if bcrypt.checkpw(password, i['password']):
                is_valid = True
                password = db_password
                break
    if not is_valid:
        return None
    auth_token = str(random.random())
    m = hashlib.sha256()
    m.update(auth_token.encode())
    print(listdir('.'))
    response = SUCCESS_RESPONSE.format(
        type='text/html; charset=utf-8; HttpOnly',
        len=num_bytes('./public/index.html')) + '\r\n'
    cookie = f'auth={auth_token}; Max-Age=69420; HttpOnly'
    response += f'Set-Cookie: {cookie}\r\n\r\n'
    current_user = {'username': username, 'password': password}
    users.find_one({}, current_user)
    users.update_one(current_user, {'$set': {'auth': m.digest()}})
    print('updated the collection with a user')
    printCollection(users)
    return response.encode()

def get_username(request, db):
    usersdb = db['users']
    auth_token = str(request.cookies.get('auth', ''))
    user = ""
    if auth_token == '':
        user = b'guest'
    else:
        m = hashlib.sha256()
        m.update(auth_token.encode())
        print('USER DB')
        printCollection(usersdb)
        user = usersdb.find_one({'auth': m.digest()})['username']
    return user
