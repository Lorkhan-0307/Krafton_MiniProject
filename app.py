from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from flask_jwt_extended.exceptions import NoAuthorizationError
from bson.objectid import ObjectId

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydatabase'  # MongoDB URI 설정
app.config['SECRET_KEY'] = 'super-secret'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)

mongo = PyMongo(app)
jwt = JWTManager(app)

documents = mongo.db.documents

@app.route('/', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/', methods=['POST'])
def login():
    data = request.form
    user_collection = mongo.db.users
    user = user_collection.find_one({'userId': data['userId']})
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity={'userId': user['userId']})
    return jsonify(access_token=access_token), 200

@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

@app.route('/redirection', methods=['GET'])
def redirection_page():
    return render_template('redirection.html')

# wiki.html로 db 올리기.
@app.route('/wiki', methods=['GET'])
def wiki_page():
    documents_all_date = list(mongo.db.documents.find({}).sort('created_at', -1))
    documents_all_like = list(mongo.db.documents.find({}).sort('likes', -1))

        # week0의 날짜,좋아요 순으로 정렬해서 table로 보냄
    documents_week0_date = list(mongo.db.documents.find({'theme':'week0'}).sort({'created_at':-1}))
    documents_week0_like = list(mongo.db.documents.find({'theme':'week0'}).sort({'likes':-1}))

        # week01의 날짜,좋아요 순으로 정렬해서 table로 보냄
    documents_week1_date = list(mongo.db.documents.find({'theme':'week1'}).sort({'created_at':-1}))
    documents_week1_like = list(mongo.db.documents.find({'theme':'week1'}).sort({'likes':-1}))

        # week2의 날짜,좋아요 순으로 정렬해서 table로 보냄
    documents_week2_date = list(mongo.db.documents.find({'theme':'week2'}).sort({'created_at':-1}))
    documents_week2_like = list(mongo.db.documents.find({'theme':'week2'}).sort({'likes':-1}))

    return render_template('wiki.html',
    documents_all_date=documents_all_date, documents_all_like=documents_all_like,
    documents_week0_date=documents_week0_date,documents_week0_like=documents_week0_like,
    documents_week1_date=documents_week1_date, documents_week1_like=documents_week1_like,
    documents_week2_date=documents_week2_date, documents_like=documents_week2_like
    ) 

@app.route('/signup', methods=['POST'])
def signup():
    data = request.form
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    user_collection = mongo.db.users
    if user_collection.find_one({'username': data['username']}):
        return jsonify({'message': 'User already exists'}), 400
    user_collection.insert_one({'username': data['username'], 'password': hashed_password})
    return redirect(url_for('login_page'))

@app.route('/write_page', methods=['GET'])
def write_page():
    return render_template('write.html')

@app.route('/write', methods=['POST'])
@jwt_required()
def write():
    try:
        verify_jwt_in_request()
        print('okay!')
        return jsonify({"redirect_url": url_for('write_page')})

    except:
        return jsonify({"redirect_url": url_for('login_page')})



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

@app.route('/verification', methods=['GET'])
@jwt_required()
def verification():
    try:
        verify_jwt_in_request()
        current_user = get_jwt_identity()
        
        username = current_user['username']
        return jsonify(logged_in_as=username)
    
    except NoAuthorizationError:
        return redirect(url_for('login_page'))

@app.route('/save', methods=['POST'])
def save():
    try:
        verify_jwt_in_request()
        data = request.get_json()
        title = data['title']
        tag = data['tag']
        writer = data['writer']
        content = data['content']

        '''
        #### TextList
            - Key
            - Title
            - Theme(For Navigation)
            - Content
            - Writer
            - isEditable(수정 가능한지)
            - created_at
            - approved_at
            - updated_at
            - isUpdated -> bool -> 검토가 필요한지
        '''

        document = {
            'title': title,
            'tag': tag,
            'writer': writer,
            'content': content,
            'created_at': datetime.utcnow()  # 저장 시간을 추가
        }
        documents.insert_one(document)

        '''
        Client받기 : Title, Theme, Content, Writer, isEditable
        생성하기: created at or updated at
        DB받기 : approved_at, isUpdated
        
        '''

        
        
        # 여기서 데이터를 데이터베이스에 저장하거나 다른 작업을 수행합니다.
        print(f"Title: {title}, Tag: {tag}, Writer: {writer}, Content: {content}")
        
        return jsonify({"message": "Data saved successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400



# 특정 게시물의 ID값을 받아 내용을 전달.
@app.route('/wiki/read', methods=['GET'])
def read_articles():
    data = request.args
    id_receive = data['id_give']

    id_receive = request.args.get('id_give')
    try:
        # ObjectId로 변환
        article_id = ObjectId(id_receive)
    except:
        return "Invalid ID format", 400
    
    article = mongo.db.documents.find_one({'_id':article_id})

    return render_template('wiki/r.html', article=article)

@app.route('/wiki/like', methods=['POST'])
def like_article():
    #클라이언트로부터 _id 받기.
    id_receive = request.form['id_give']
    article_id = ObjectId(id_receive)

    article = mongo.db.documents.find_one({'_id':article_id})
    
    #받은 id에 해당하는 like +1
    new_like = article['likes'] + 1
    
    #몽고db에 업데이트
    mongo.db.documents.update_one({'_id': article_id}, {'$set': {'likes': new_like}})

    return jsonify({'result': 'success', 'msg': 'success'})

#랜덤 게시물은 나중에 추가.
# @app.route('/wiki/random', methods=['GET'])
# def random_articles():
#     articles = list(mongo.db.documents.find({}))
#     ranNum = random.randrange(0,len(articles) - 1)
#     article = articles[ranNum]

#     return render_template('wiki/r.html', article = article)

#  겹치는 타이틀이 있는지 없는지.
@app.route('/wiki/w', methods=['GET'])
def write_new_title():
    title_receive = request.args['title_give']
    if mongo.db.documents.count_documents({'Title': title_receive}, limit=1) > 0:
        return jsonify({'message': '타이틀이 이미 존재합니다. 다른 타이틀을 골라주세요.','result' : 'fail'}), 403
    
    return jsonify({'message': '타이틀이 유효합니다.', 'result': 'success'}), 200

# # 몽고 디비 도큐먼트 데이더베이스 연습 코드
# a = {
#     'writer':'john',
#     'created_at':'2024.07.03',
#     'tag':'python',
#     'likes': 3,
#     'theme':'week0'
# }
# b = {
#     'writer':'john',
#     'created_at':'2024.07.03',
#     'tag':'python2',
#     'likes': 2,
#     'theme':'week1'
# }
# mongo.db.documents.insert_one(a)
# mongo.db.documents.insert_one(b)

if __name__ == '__main__':
    app.run(debug=True)