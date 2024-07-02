from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from flask_jwt_extended.exceptions import NoAuthorizationError

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydatabase'  # MongoDB URI 설정
app.config['SECRET_KEY'] = 'super-secret'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

mongo = PyMongo(app)
jwt = JWTManager(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

@app.route('/redirection', methods=['GET'])
def redirection_page():
    return render_template('redirection.html')

@app.route('/wiki', methods=['GET'])
def wiki_page():
    return render_template('wiki.html')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.form
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    user_collection = mongo.db.users
    if user_collection.find_one({'username': data['username']}):
        return jsonify({'message': 'User already exists'}), 400
    user_collection.insert_one({'username': data['username'], 'password': hashed_password})
    return redirect(url_for('login_page'))

@app.route('/login', methods=['POST'])
def login():
    data = request.form
    user_collection = mongo.db.users
    user = user_collection.find_one({'username': data['username']})
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity={'username': user['username']})
    return jsonify(access_token=access_token), 200


@app.route('/wiki', methods=['POST'])
@jwt_required()
def wiki():
    try:
        verify_jwt_in_request()
        current_user = get_jwt_identity()
        
        username = current_user['username']
        print(username)
        return jsonify(logged_in_as=username)
    
    except NoAuthorizationError:
        return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=True)
