#!/usr/bin/env python3

import sys
import json

import requests

nickname = sys.argv[1]
server = 'http://localhost:5000'

def register_user(nickname):
    data = json.dumps({'nickname': nickname})
    requests.post(f'{server}/users', data = data, headers = {'Content-Type': 'application/json'})

def deregister_user(nickname):
    requests.delete(f'{server}/users/{nickname}')

def list_users():
    r = requests.get(f'{server}/users')
    users = r.json()
    return users

def list_messages():
    return requests.get(f'{server}/chat').json()

def send_message(message):
    requests.post(f'{server}/chat', data = json.dumps({'message': message}), headers = {'Content-Type': 'application/json'})

def main():
    register_user(nickname)

    for line in sys.stdin:
        message = line.rstrip('\n')

        if message == '!users':
            users = list_users()
            print(users)
            continue

        if message == '!logout':
            deregister_user(nickname)
            break

        if message == '!messages':
            messages = list_messages()
            print(messages)
            continue

        if message:
            send_message(message)

if __name__ == '__main__':
    main()
