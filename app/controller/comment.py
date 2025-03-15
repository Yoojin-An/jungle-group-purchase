from flask import router, Blueprint, jsonify, request
from datetime import datetime, timedelta, timezone
from bson.objectid import ObjectId
from core.auth import Auth as auth
from core.database import Database as db
from alarm import Alarm 
from run import scheduler

router = Blueprint("comment", __name__, url_prefix="/comment")

@router.route('/', methods=['POST'])
@auth.jwt_required
def create_comment():
    alarm = Alarm()

    user_name = auth.decode_token("name")
    post_id = ObjectId(request.form['post_id'])
    text = request.form['text']

    comment = {
        "_id" : str(datetime.now(timezone.utc).timestamp()*1000),
        "participantId" : user_name,
        "text": text,
        "created_at": datetime.now(timezone.utc),
        "updated_at": 0,
        "status" : 'valid',
        "replies": [],
    }

    result = db.posts.update_one(
        {"_id": post_id},
        {"$push": {"comments": comment}}
    )

    # 시연용 스케쥴러
    run_time = datetime.now() + timedelta(seconds=10)
    scheduler.add_job(alarm.check_expired_products, 'date', run_date=run_time)

    if result.modified_count > 0:
        return jsonify({"result": "success", "message": "댓글이 추가되었습니다."})
    else:
        return jsonify({"result": "fail", "message": "게시글을 찾을 수 없습니다."})

@router.route('/<id>', methods=["GET"])
def read_comment(id):
        product_id = ObjectId(id)  # 유효한 ObjectId로 변환
        products = db.posts.find_one({"_id": product_id})
        comments = products["comments"]
        for i in range(len(products["comments"])):
            comments[i]["_id"] = str(comments[i]["_id"])  # _id를 문자열로 변환하여 반환
        return jsonify({"result": "success", "response": comments})

@router.route('/', methods=['PATCH']) 
def update_comment():
    comment_id = request.form['comment_id']  
    text = request.form['update_text']

    result = db.posts.update_one(
        {"comments._id": comment_id},
        {"$set": {"comments.$.text": text, "comments.$.updated_at": datetime.now(timezone.utc)}}
    )

    if result.modified_count > 0:
        return jsonify({"result": "success", "message": "댓글이 수정되었습니다."})

@router.route('/', methods=['PUT']) 
def delete_comment():
    comment_id = request.form['comment_id']  
    result = db.posts.update_one(
        {"comments._id": comment_id },
        {"$set": {"comments.$.status": "deleted" }}
    )

    if result.modified_count > 0:
        return jsonify({"result": "success", "message": "댓글이 삭제되었습니다."})

@router.route('/reply', methods=['POST'])
def create_reply():
    user_name = auth.decode_name()
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

    result = db.posts.update_one(
        {"_id": post_id, "comments._id": comment_id},
        {"$push": { "comments.$.replies" : new_reply}}
    )

    if result.modified_count > 0:
        return jsonify({"result": "success", "message": "대댓글이 추가되었습니다."})
    else:
        return jsonify({"result": "fail", "message": "댓글을 찾을 수 없습니다."})
    
@router.route('/reply/<id>', methods=["GET"])
def read_reply(id):
        product_id = ObjectId(id)  # 유효한 ObjectId로 변환
        comment_id = request.form['comment_id']  # 부모 댓글 ID
        comments = db.posts.find_one({"_id" : product_id, "comments._id": comment_id})
        replies = comments["replies"]
        return jsonify({"result": "success", "response": replies})

@router.route('/reply', methods=['POST'])
def update_reply():
    post_id = ObjectId(request.form['post_id'])
    comment_id = request.form['comment_id']
    reply_id = request.form['reply_id']
    text = request.form['text'] # 수정된 대댓글

    result = db.posts.update_one(
        {"_id" : post_id, "comments._id": comment_id, "comments.replies._id" : reply_id},
        {"$set": {
            "comments.$.replies.$[elem].text": text,
            "comments.$.replies.$[elem].updated_at": datetime.now(timezone.utc)
        }},
        array_filters=[{"elem._id": reply_id}]  
    )

    if result.modified_count > 0:
        return jsonify({"result": "success", "message": "대댓글이 수정정되었습니다."})
    
@router.route('/reply', methods=['PATCH'])
def delete_reply():
    post_id = ObjectId(request.form['post_id'])
    comment_id = request.form['comment_id']
    reply_id = request.form['reply_id']

    result = db.posts.update_one(
        {"_id": post_id, "comments._id": comment_id, "comments.replies._id": reply_id},
        {"$set": {"comments.$.replies.$[elem].status": "deleted"}},
        array_filters=[{"elem._id": reply_id}]
    )

    if result.modified_count > 0:
        return jsonify({"result": "success", "message": "대댓글이 삭제되었습니다."})
    else:
        return jsonify({"result": "fail", "message": "대댓글을 찾을 수 없습니다."})
