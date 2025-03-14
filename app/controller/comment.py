
''' 
댓글 대댓글 기능 구현
''' 

@app.route('/new_comment', methods=['POST']) #id는 자동생성되는 친구 쓰는거로~
@jwt_required
def new_comment():
    user_name = decode_name()
    print(request.form['post_id'])
    post_id = ObjectId(request.form['post_id'])  # 댓글을 추가할 게시글 ID
    #comment_author = 댓글 작성장의 슬렉 계정정
    text = request.form['text']

    comment = {
        "_id" : str(datetime.now(timezone.utc).timestamp()*1000),
        #'comment_author_id": comment_author,
        "participantId" : user_name,
        "text": text,
        "created_at": datetime.now(timezone.utc),
        "updated_at": 0,
        "status" : 'valid',
        "replies": [],  # 대댓글 
        
    }

    # 게시글 컬렉션에 저장
    result = db.boards.update_one(
        {"_id": post_id},
        {"$push": {"comments": comment}}
    )

    # 시연용 스케쥴러
    run_time = datetime.now() + timedelta(seconds=10)
    scheduler.add_job(check_expired_products, 'date', run_date=run_time)

    if result.modified_count > 0:
        return jsonify({"result": "success", "message": "댓글이 추가되었습니다."})
    else:
        return jsonify({"result": "fail", "message": "게시글을 찾을 수 없습니다."})
    
@app.route('/read_comment/<id>', methods=["GET"])
def read_comment(id):
        product_id = ObjectId(id)  # 유효한 ObjectId로 변환
        products = db.boards.find_one({"_id": product_id})
        comments = products["comments"]
        for i in range(len(products["comments"])):
            comments[i]["_id"] = str(comments[i]["_id"])  # _id를 문자열로 변환하여 반환
        return jsonify({"result": "success", "response": comments})

@app.route('/update_comment', methods=['POST']) 
def Update_comment():
    comment_id = request.form['comment_id']  
    text = request.form['update_text']

    result = db.boards.update_one(
        {"comments._id": comment_id},
        {"$set": {"comments.$.text": text, "comments.$.updated_at": datetime.now(timezone.utc)}}
    )



    if result.modified_count > 0:
        return jsonify({"result": "success", "message": "댓글이 수정되었습니다."})

@app.route('/delete_comment', methods=['POST']) 
def delete_comment():
    comment_id = request.form['comment_id']  
    result = db.boards.update_one(
        {"comments._id": comment_id },
        {"$set": {"comments.$.status": "deleted" }}
    )

    if result.modified_count > 0:
        return jsonify({"result": "success", "message": "댓글이 삭제되었습니다."})

''' 대댓글 생성 ''' 
@app.route('/new_reply', methods=['POST'])
def New_reply():
    user_name = decode_name()
    print("1", user_name)
    post_id = ObjectId(request.form['post_id'])  # 게시글 ID
    comment_id = request.form['comment_id']  # 부모 댓글 ID
    # reply_author = 슬렉 계정 사용자
    text = request.form['text']

    new_reply = {
        "_id" : str(datetime.now(timezone.utc).timestamp()*1000),
        #"author_id": reply_author,
        "text": text,
        "created_at": datetime.now(timezone.utc),
        "updated_at" : 0,
        "status" : 'valid',
        "user_name" : user_name
    }

    result = db.boards.update_one(
        {"_id": post_id, "comments._id": comment_id},
        {"$push": { "comments.$.replies" : new_reply}}
    )

    if result.modified_count > 0:
        return jsonify({"result": "success", "message": "대댓글이 추가되었습니다."})
    else:
        return jsonify({"result": "fail", "message": "댓글을 찾을 수 없습니다."})
    
@app.route('/read_replies/<id>', methods=["GET"])
def read_replies(id):
        product_id = ObjectId(id)  # 유효한 ObjectId로 변환
        comment_id = request.form['comment_id']  # 부모 댓글 ID
        comments = db.boards.find_one({"_id" : product_id, "comments._id": comment_id})
        replies = comments["replies"]
        print("2", comments["replies"][0]["user_name"])
        return jsonify({"result": "success", "response": replies})

@app.route('/update_reply', methods=['POST'])
def Update_reply():
    post_id = ObjectId(request.form['post_id'])  # 게시글 ID
    comment_id = request.form['comment_id']  # 부모 댓글 ID
    reply_id = request.form['reply_id'] #대댓글 ID
    # reply_author = 슬렉 계정 사용자
    text = request.form['text'] # 수정된 대댓글글

    result = db.boards.update_one(
        {"_id" : post_id, "comments._id": comment_id, "comments.replies._id" : reply_id},
        {"$set": {
            "comments.$.replies.$[elem].text": text,
            "comments.$.replies.$[elem].updated_at": datetime.now(timezone.utc)
        }},
        array_filters=[{"elem._id": reply_id}]  
    )

    if result.modified_count > 0:
        return jsonify({"result": "success", "message": "대댓글이 수정정되었습니다."})
    
@app.route('/delete_reply', methods=['POST'])
def delete_reply():
    post_id = ObjectId(request.form['post_id'])
    comment_id = request.form['comment_id']
    reply_id = request.form['reply_id']

    result = db.boards.update_one(
        {"_id": post_id, "comments._id": comment_id, "comments.replies._id": reply_id},
        {"$set": {"comments.$.replies.$[elem].status": "deleted"}},
        array_filters=[{"elem._id": reply_id}]
    )

    if result.modified_count > 0:
        return jsonify({"result": "success", "message": "대댓글이 삭제되었습니다."})
    else:
        return jsonify({"result": "fail", "message": "대댓글을 찾을 수 없습니다."})
