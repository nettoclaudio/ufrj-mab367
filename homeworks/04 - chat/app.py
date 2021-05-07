#!/usr/bin/env python3

from flask import Flask, jsonify, request


app = Flask(__name__)

users = []
messages = []

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/users', methods=['GET'])
def list_users():
    return jsonify(users)

@app.route('/users', methods=['POST'])
def register_user():
    user = request.get_json()
    if not user:
        return 'the input data must be an object', 400

    for u in users:
        if u.get('nickname') == user.get('nickname'):
            return 'an user alreday is using the nickname', 422

    users.append(user)

    return '', 201

@app.route('/users/<nickname>', methods=['DELETE'])
def deregister_user(nickname):
    if not nickname:
        return 'nickname must be provided', 400

    for index, user in enumerate(users):
        if user.get('nickname') == nickname:
            users.pop(index)
            return '', 200

    return '', 404

@app.route('/chat', methods=['GET'])
def get_messages():

    print(messages)

    return jsonify(messages)

@app.route('/chat', methods=['POST'])
def send_message():
    message = request.get_json()

    print(message)

    messages.append(message)
    return '', 200

if __name__ == '__main__':
    app.run(debug=True)
