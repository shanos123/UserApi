from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app, resources={r"/users/*": {"origins": "*"}})  # Allow all origins for /users endpoint

# Path to the JSON file
USERS_FILE = 'users.json'

def read_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as file:
            return json.load(file)
    return {}

def write_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file, indent=4)

def get_next_user_id(users):
    if not users:
        return 1
    last_id = max(int(user_id) for user_id in users.keys())
    return last_id + 1

@app.route('/users/all', methods=['GET'])
def get_all_users():
    """
    Endpoint to get all users.
    """
    try:
        users = read_users()
        return jsonify(users), 200
    except Exception as e:
        app.logger.error(f"Error fetching users: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500
    
@app.route('/users', methods=['POST', 'GET'])
def create_user():
    if request.method == 'GET':
        users = read_users()
        return jsonify(users)

    elif request.method == 'POST':
        try:
            users = read_users()
            user_id = str(get_next_user_id(users))
            user_data = request.json
            app.logger.info(f"Received user data: {user_data}")

            if not user_data:
                return jsonify({'error': 'Invalid data'}), 400

            users[user_id] = user_data
            write_users(users)
            return jsonify({'message': 'User created', 'user': {user_id: user_data}}), 201
        except Exception as e:
            app.logger.error(f"Error creating user: {e}")
            return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/users/<user_id>', methods=['GET'])
def read_user(user_id):
    users = read_users()
    user = users.get(user_id)
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({user_id: user}), 200

@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    users = read_users()
    if user_id not in users:
        return jsonify({'message': 'User not found'}), 404
    user_data = request.json
    users[user_id] = user_data
    write_users(users)
    return jsonify({'message': 'User updated', 'user': {user_id: user_data}}), 200

@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    users = read_users()
    if user_id not in users:
        return jsonify({'message': 'User not found'}), 404
    del users[user_id]
    write_users(users)
    return jsonify({'message': 'User deleted'}), 200

@app.route('/users/login', methods=['POST'])
def login_user():
    try:
        users = read_users()
        login_data = request.json
        username = login_data.get('username')
        password = login_data.get('password')

        for user in users.values():
            if user.get('username') == username and user.get('password') == password:
                return jsonify({'message': 'Login success'}), 200

        return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        app.logger.error(f"Error during login: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
