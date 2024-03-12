import json
import hashlib
import sys
from bson.objectid import ObjectId
import html

from util.constants import SUCCESS_RESPONSE, ERROR_RESPONSE
from util.constants import printCollection
import util.auth
import util.constants
from util.constants import to_str

def chat_message(request, db):
    chat_collection = db['chat']
    user = util.auth.get_username(request, db)
    # users = db['users']
    # auth_token = str(request.cookies.get('auth', ''))
    # user = ""
    # if auth_token == '':
    #     user = b'guest'
    # else:
    #     m = hashlib.sha256()
    #     m.update(auth_token.encode())
    #     print('USER DB')
    #     printCollection(users)
    #     user = users.find_one({'auth': m.digest()})['username']
    if user != "" and user != None:
        username = user.decode()
        if request.body == None or to_str(request.body) == '':
            return
        msg_json = {}
        try:
            msg_json = json.loads(util.constants.to_str(request.body))
        except json.JSONDecodeError:
            print(request.body)
        msg = html.escape(msg_json['message'])
        new_field = {'username': username, 'message': msg}
        id = chat_collection.insert_one(new_field).inserted_id
        print('id of new message', id)
    else:
        print('chat message')
        new_field = {'username': 'guest', 'message': msg}
        id = chat_collection.insert_one(new_field).inserted_id
    print('printing chat_collection :D')
    printCollection(chat_collection)

def chat_history(db):
    chat_collection = db['chat']
    msgs = []
    for dbchat in chat_collection.find({}):
        chat = {}
        for key, item in dbchat.items():
            if key == '_id':
                key = 'id'
            chat[key] = str(item)
        msgs.append(chat)
    msgs_response = json.dumps(msgs)
    response = SUCCESS_RESPONSE.format(
        type='application/json', len=len(msgs_response))
    response += '\r\n\r\n'
    response += msgs_response
    return response.encode('utf-8')

def delete_chat(request, db):
    chatdb = db['chat']
    target_chat_id = request.path.split('/')[-1]
    target_chat = chatdb.find_one({'_id': ObjectId(target_chat_id)})
    # chatdb.delete_one({'_id': ObjectId(target_chat_id)})
    if target_chat == None:
        raise ModuleNotFoundError
    current_user = util.auth.get_username(request, db).decode()
    if target_chat['username'] == current_user:
        chatdb.delete_one({'_id': ObjectId(target_chat_id)})

        response = SUCCESS_RESPONSE.format(type="text/plain", len=4)
        response += '\r\n\r\ndone'
        return response.encode()
    response = 'HTTP/1.1 403 Wrong User\r\nContent-Type: text/plain\r\n'
    response += 'Content-Length: 10\r\nContent-Type-Options: nosniff\r\n\r\n'
    response += 'wrong user'
    return response.encode()
