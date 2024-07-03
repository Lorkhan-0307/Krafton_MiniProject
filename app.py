from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, create_access_token, get_jwt, jwt_required, get_jwt_identity, verify_jwt_in_request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended.exceptions import NoAuthorizationError
from bson.objectid import ObjectId
from datetime import datetime as dt
import datetime

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydatabase'  # MongoDB URI 설정
app.config['SECRET_KEY'] = 'super-secret'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)


themesList = [
    ("ProgrammingLanguage", "프로그래밍 언어"),
    ("DataStructure", "자료구조"),
    ("Algorithm", "알고리즘"),
    ("OperatingSystem", "운영체제"),
    ("ComputerArchitecture", "컴퓨터구조"),
    ("Database", "데이터베이스"),
    ("LogicCircuit", "논리회로"),
    ("ComputerNetwork", "컴퓨터 네트워크"),
    ("Others", "기타")
]

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


    access_token = create_access_token(identity={'userId': user['userId'], 'userRealName': user['userrealname'], 'userNickName': user['usernickname']})
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
        # ProgrammingLanguage의 날짜,좋아요 순으로 정렬해서 table로 보냄
    documents_ProgrammingLanguage_date = list(mongo.db.documents.find({'theme':'ProgrammingLanguage'}).sort('created_at', -1))
    documents_ProgrammingLanguage_like = list(mongo.db.documents.find({'theme':'ProgrammingLanguage'}).sort('recommended', -1))

        # DataStructure의 날짜,좋아요 순으로 정렬해서 table로 보냄
    documents_DataStructure_date = list(mongo.db.documents.find({'theme':'DataStructure'}).sort('created_at', -1))
    documents_DataStructure_like = list(mongo.db.documents.find({'theme':'DataStructure'}).sort('recommended', -1))

        # Algorhythm의 날짜,좋아요 순으로 정렬해서 table로 보냄
    documents_Algorhythm_date = list(mongo.db.documents.find({'theme':'Algorhythm'}).sort('created_at', -1))
    documents_Algorhythm_like = list(mongo.db.documents.find({'theme':'Algorhythm'}).sort('recommended', -1))

        # 의 날짜,좋아요 순으로 정렬해서 table로 보냄
    documents_OperatingSystem_date = list(mongo.db.documents.find({'theme':'OperatingSystem'}).sort('created_at', -1))
    documents_OperatingSystem_like = list(mongo.db.documents.find({'theme':'OperatingSystem'}).sort('recommended', -1))
    
        # 의 날짜,좋아요 순으로 정렬해서 table로 보냄
    documents_Computerarchitecture_date = list(mongo.db.documents.find({'theme':'Computerarchitecture'}).sort('created_at', -1))
    documents_Computerarchitecture_like = list(mongo.db.documents.find({'theme':'Computerarchitecture'}).sort('recommended', -1))

        # 의 날짜,좋아요 순으로 정렬해서 table로 보냄
    documents_Database_date = list(mongo.db.documents.find({'theme':'Database'}).sort('created_at', -1))
    documents_Database_like = list(mongo.db.documents.find({'theme':'Database'}).sort('recommended', -1))

        # 의 날짜,좋아요 순으로 정렬해서 table로 보냄
    documents_LogitCircuit_date = list(mongo.db.documents.find({'theme':'LogitCircuit'}).sort('created_at', -1))
    documents_LogitCircuit_like = list(mongo.db.documents.find({'theme':'LogitCircuit'}).sort('recommended', -1))

        # 의 날짜,좋아요 순으로 정렬해서 table로 보냄
    documents_ComputerNetwork_date = list(mongo.db.documents.find({'theme':'ComputerNetwork'}).sort('created_at', -1))
    documents_ComputerNetwork_like = list(mongo.db.documents.find({'theme':'ComputerNetwork'}).sort('recommended', -1))

        # 의 날짜,좋아요 순으로 정렬해서 table로 보냄
    documents_Others_date = list(mongo.db.documents.find({'theme':'Others'}).sort('created_at', -1))
    documents_Others_like = list(mongo.db.documents.find({'theme':'Others'}).sort('recommended', -1))


    return render_template('wiki.html',  themesList=themesList,
                            documents_ProgrammingLanguage_date=documents_ProgrammingLanguage_date,
                            documents_ProgrammingLanguage_like=documents_ProgrammingLanguage_like,
                            documents_DataStructure_date=documents_DataStructure_date,
                            documents_DataStructure_like=documents_DataStructure_like,
                            documents_Algorhythm_date=documents_Algorhythm_date,
                            documents_Algorhythm_like=documents_Algorhythm_like,
                            documents_OperatingSystem_date=documents_OperatingSystem_date, 
                            documents_OperatingSystem_like=documents_OperatingSystem_like,
                            documents_Computerarchitecture_date=documents_Computerarchitecture_date,
                            documents_Computerarchitecture_like=documents_Computerarchitecture_like,
                            documents_Database_date=documents_Database_date,
                            documents_Database_like=documents_Database_like,
                            documents_LogitCircuit_date=documents_LogitCircuit_date,
                            documents_LogitCircuit_like=documents_LogitCircuit_like,
                            documents_ComputerNetwork_date=documents_ComputerNetwork_date,
                            documents_ComputerNetwork_like=documents_ComputerNetwork_like,
                            documents_Others_date=documents_Others_date,
                            documents_Others_like=documents_Others_like
    ) 

@app.route('/signup', methods=['POST'])
def signup():
    data = request.form

    # 비밀번호 및 비밀번호 확인 비교
    if(data['password'] != data['passwordCheck']):
        return jsonify({'message': 'Password incorrect with Password Check'}), 400


    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    userrealname = data['realname']
    usernickname = data['nickname']
    useridentification = data['phoneNum']
    
    if(userrealname == "이승민" or userrealname == "최자영" or userrealname == "진재웅"):
        userauthorization = "Admin"
    else :
        userauthorization = "User"

    user_collection = mongo.db.users
    if user_collection.find_one({'userId': data['userId']}):
        return jsonify({'message': 'User already exists'}), 400
    if user_collection.find_one({'userNickName': data['nickname']}):
        return jsonify({'message': 'User Nickname already exists'}), 400
    
    # Todo : 사용자 검증 들어가야함

    user_collection.insert_one({'userId': data['userId'], 'password': hashed_password, 'userrealname' : userrealname, 
                                'usernickname': usernickname, 'useridentification': useridentification,
                                'userauthorization': userauthorization})
    return redirect(url_for('login_page'))

@app.route('/write_page', methods=['GET'])
def write_page():
    return render_template('write.html', themesList=themesList)

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
        userNickName = current_user['userNickName']
        return jsonify(logged_in_as=userNickName)
    
    except NoAuthorizationError:
        return redirect(url_for('login_page'))

@app.route('/verification', methods=['GET'])
@jwt_required()
def verification():
    try:
        verify_jwt_in_request()
        current_user = get_jwt_identity()
        
        userNickName = current_user['userNickName']
        return jsonify(logged_in_as=userNickName)
    
    except NoAuthorizationError:
        return redirect(url_for('login_page'))
    
@app.route('/getWrittenNum', methods=['POST'])
def getWrittenNum(userNickname):
    return documents.count_documents({'writer': userNickname})



@app.route('/getUserData', methods=['GET'])
@jwt_required()
def get_user_data():
    claims = get_jwt()
    user_info = claims['sub']
    userRealname = user_info.get('userRealName')
    userNickname = user_info.get('userNickName')
    userWrittenNum = documents.count_documents({'writer': userNickname})
    return jsonify(userRealname=userRealname, userNickname=userNickname, userWrittenNum = userWrittenNum)


@app.route('/save', methods=['POST'])
@jwt_required()
def save():
    try:
        verify_jwt_in_request()
        data = request.get_json()
        title = data['title']
        writer = data['writer']
        content = data['content']
        theme = data['theme']
        isEditable = data['isEditable']

         # 현재 시간 설정
        try:
            now_dt = dt.now()
            print("Current time (datetime):", now_dt)
        except Exception as e:
            print("Error getting current time:", str(e))
            return jsonify({"error": "Error getting current time"}), 500

        # 마이크로초 생략하고 포맷 지정
        formatted_now = now_dt.strftime('%Y-%m-%d %H:%M:%S')
        print("Formatted current time:", formatted_now)

        created_at = formatted_now
        approved_at = formatted_now
        updated_at = formatted_now

        isUpdated = False
        recommended = 0


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
                -> isUpdated가 참이면 approve 가 필요하다.
        '''

        document = {
            'title': title,
            'writer': writer,
            'content': content,
            'isEditable': isEditable,
            'theme': theme,
            'created_at': created_at,
            'approved_at': approved_at,
            'updated_at': updated_at,
            'isUpdated': isUpdated,
            'recommended': recommended
        }

        print(document)

        documents.insert_one(document)

        '''
        Client받기 : Title, Theme, Content, Writer, isEditable
        생성하기: created at or updated at
        DB받기 : approved_at, isUpdated
        '''
        return jsonify({"message": "Data saved successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400



# 특정 게시물의 ID값을 받아 내용을 전달.
@app.route('/wiki/r/<id>', methods=['GET'])
def view_post(id):
    # post = documents.find_one({'title':title})
    # if not post:
    #     return jsonify({"msg": "Post not found"}), 404
    # new_title = post['title'].split('_')[0]
    # create_at = post['create_at']
    # likes = post['likes']
    # theme = post['theme']
    # content = post['content']

    # return render_template('post.html', post=post, new_title=new_title,
    #                        create_at=create_at,likes=likes,theme=theme,content=content)
    post = documents.find_one({'_id': ObjectId(id)})
    created_at = post['created_at']
    recommended = post['recommended']
    theme = post['theme']
    cnt = documents.count_documents({})

    return render_template('post.html', post=post,
                           create_at=created_at,recommended=recommended,theme=theme,cnt=cnt)

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
if __name__ == '__main__':
    app.run(debug=True)