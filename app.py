from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, create_access_token, get_jwt, jwt_required, get_jwt_identity, verify_jwt_in_request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended.exceptions import NoAuthorizationError
from bson.objectid import ObjectId
from datetime import datetime as dt
import datetime
import markdown
import math

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
edited_documents = mongo.db.edited_documents

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

@app.route('/wiki/<theme>', methods=['GET'])
def wiki_redirect(theme):
    documents_theme_date = documents.find({'theme':theme}).sort('created_at', -1).limit(5)
    documents_theme_like = documents.find({'theme':theme}).sort('recommended', -1).limit(5)
    return render_template('wiki.html',themesList=themesList, documents_theme_date=documents_theme_date, documents_theme_like=documents_theme_like)

# wiki.html로 db 올리기.
@app.route('/wiki', methods=['GET'])
def wiki_page():
    
    documents_theme_date = documents.find().sort('created_at', -1).limit(5)
    documents_theme_like = documents.find().sort('recommended', -1).limit(5)

    return render_template('wiki.html',  themesList=themesList,documents_theme_date=documents_theme_date, documents_theme_like=documents_theme_like)

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

@app.route('/wiki/ongoing', methods=['GET'])
def wiki_ongoing_page():
    return render_template('wiki_ongoing.html', themesList=themesList)

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


@app.route('/editsave', methods=['POST'])
@jwt_required()
def edit_save():
    try:
        verify_jwt_in_request()
        data = request.get_json()
        title = data['title']

        post = documents.find_one({'title': title, 'isEditable': True})
        original_post_id = str(post['_id'])
        writer = data['writer']
        original_writer = data['original_writer']
        content = data['content']
        theme = data['theme']
        isEditable = data['isEditable']
        created_at = post['created_at']
        approved_at = post['approved_at']

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

        updated_at = formatted_now

        isUpdated = True
        recommended = post['recommended']


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
            'original_post_id': original_post_id,
            'original_writer': original_writer,
            'content': content,
            'isEditable': isEditable,
            'theme': theme,
            'created_at': created_at,
            'approved_at': approved_at,
            'updated_at': updated_at,
            'isUpdated': isUpdated,
            'recommended': recommended,
            'approveCnt' : 0,
            'denyCnt' : 0
        }


        edited_documents.insert_one(document)

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
    post = documents.find_one({'_id': ObjectId(id)})
    content = markdown.markdown(post['content'])
    created_at = post['created_at']
    recommended = post['recommended']
    theme = post['theme']
    cnt = documents.count_documents({})

    return render_template('read.html', post=post, content=content
                           ,create_at=created_at,recommended=recommended,theme=theme,cnt=cnt)



# 특정 게시물의 ID값을 받아 내용을 전달.
@app.route('/wiki/e/<id>', methods=['GET'])
def edit_page(id):
    post = documents.find_one({'_id': ObjectId(id)})

    # 만약 isEditing인가 뭔가가 참이면 edit이 아니고 readedit page로 넘어가야함.
    if post.get('isUpdated', False):
        return redirect(url_for('readedit_page', id=id))

    content = post['content']
    created_at = post['created_at']
    recommended = post['recommended']
    theme = post['theme']
    cnt = documents.count_documents({})

    return render_template('edit_write.html', post=post, content=content
                           ,create_at=created_at,recommended=recommended,theme=theme,cnt=cnt)

@app.route('/wiki/re/<id>', methods=['GET'])
def readedit_page(id):
    post = edited_documents.find_one({'_id': ObjectId(id)})
    if(documents.find_one({'_id': ObjectId(post['original_post_id'])}) == None):
        redirect(url_for('wiki_page'))
    original_post = documents.find_one({'_id': ObjectId(post['original_post_id'])})
    if(original_post == None):
        redirect(url_for('wiki_page'))
    original_content = markdown.markdown(original_post['content'])
    content = markdown.markdown(post['content'])
    created_at = post['created_at']
    recommended = post['recommended']
    theme = post['theme']
    cnt = documents.count_documents({})

    return render_template('edit_read.html', original_content=original_content, themesList=themesList, post=post, content=content,
                           create_at=created_at, recommended=recommended, theme=theme, cnt=cnt)

@app.route('/wiki/like', methods=['POST'])
@jwt_required()
def like_article():
    verify_jwt_in_request()
    #클라이언트로부터 _id 받기.
    data = request.get_json()  # request.form 대신 request.get_json() 사용
    article_id = ObjectId(data['id_give'])  # JSON 데이터에서 id_give 추출

    article = mongo.db.documents.find_one({'_id':article_id})
    
    #받은 id에 해당하는 like +1
    new_like = article['recommended'] + 1
    
    #몽고db에 업데이트
    mongo.db.documents.update_one({'_id': article_id}, {'$set': {'recommended': new_like}})

    return jsonify({'result': 'success', 'msg': 'success'})

@app.route('/wiki/approve', methods=['POST'])
@jwt_required()
def add_approve():
    verify_jwt_in_request()
    #클라이언트로부터 _id 받기.
    data = request.get_json()  # request.form 대신 request.get_json() 사용
    article_id = ObjectId(data['id_give'])  # JSON 데이터에서 id_give 추출

    article = edited_documents.find_one({'_id':article_id})

    new_approve = article['approveCnt'] + 1
    if(new_approve >= 5):
        # 원본으로 교체
        original_post_id = article['original_post_id']
        if isinstance(original_post_id, str):
            original_post_id = ObjectId(original_post_id)


        original_article = documents.find_one({'_id': original_post_id})
        now_dt = dt.now()
        formatted_now = now_dt.strftime('%Y-%m-%d %H:%M:%S')

        approved_at = formatted_now
        document = {
            'title': article['title'],
            'writer': original_article['writer'],
            'content': article['content'],
            'isEditable':  article['isEditable'],
            'theme': article['theme'],
            'created_at': article['created_at'],
            'approved_at': approved_at,
            'updated_at': article['updated_at'],
            'isUpdated': False,
            'recommended': article['recommended']
        }
        documents.update_one(
            {'_id':original_post_id},
            {'$set': document}
        )
        edited_documents.delete_one({'_id': ObjectId(article_id)})

    else:
        edited_documents.update_one({'_id': article_id}, {'$set': {'approveCnt': new_approve}})

    return jsonify({'result': 'success', 'msg': 'success'})

@app.route('/wiki/deny', methods=['POST'])
@jwt_required()
def add_deny():
    verify_jwt_in_request()
    #클라이언트로부터 _id 받기.
    data = request.get_json()  # request.form 대신 request.get_json() 사용
    article_id = ObjectId(data['id_give'])  # JSON 데이터에서 id_give 추출
    #클라이언트로부터 _id 받기.
    data = request.get_json()  # request.form 대신 request.get_json() 사용
    article_id = ObjectId(data['id_give'])  # JSON 데이터에서 id_give 추출

    article = edited_documents.find_one({'_id':article_id})

    new_deny = article['denyCnt'] + 1
    if(new_deny >= 5):
        # 삭제
        original_post_id = article['original_post_id']
        if isinstance(original_post_id, str):
            original_post_id = ObjectId(original_post_id)


        original_article = documents.find_one({'_id': original_post_id})

        documents.update_one(
            {'_id': ObjectId(article['original_post_id'])},
            {'$set': {'isUpdated': False}}
        )
        edited_documents.delete_one({'_id': ObjectId(article_id)})

    else:
        edited_documents.update_one({'_id': article_id}, {'$set': {'denyCnt': new_deny}})

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

@app.route('/get_documents', methods=['GET'])
def get_documents():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 5))
        theme = request.args.get('theme', '')
        method = request.args.get('method', '')

        documents = mongo.db.documents
        query = {'theme': theme} if theme else {}

        total_documents = documents.count_documents(query)
        total_pages = math.ceil(total_documents / limit)

        if method == 'recommended':
            sort_field = 'recommended'
        else:
            sort_field = 'approved_at'

        documents_theme_date = list(documents.find(query).sort(sort_field, -1).skip((page - 1) * limit).limit(limit))

        # Convert ObjectId to string for JSON serialization
        for doc in documents_theme_date:
            doc['_id'] = str(doc['_id'])

        return jsonify({
            'documents': documents_theme_date,
            'total_pages': total_pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


@app.route('/get_documents_ongoing', methods=['GET'])
def get_documents_ongoing():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        theme = request.args.get('theme', '')

        edited_documents = mongo.db.edited_documents
        query = {'theme': theme} if theme else {}

        total_documents = edited_documents.count_documents(query)
        total_pages = math.ceil(total_documents / limit)

        sort_field = 'updated_at'

        documents_theme_date = list(edited_documents.find(query).sort(sort_field, -1).skip((page - 1) * limit).limit(limit))

        # Convert ObjectId to string for JSON serialization
        for doc in documents_theme_date:
            doc['_id'] = str(doc['_id'])

        return jsonify({
            'documents': documents_theme_date,
            'total_pages': total_pages,
            'current_page': page
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)