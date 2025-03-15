import request
from flask import Blueprint, jsonify, router
from bson.objectid import ObjectId
from core.database import Database as db
from core.auth import Auth as auth

router = Blueprint("comment", __name__)

@router.route('/order/<id>', methods=['POST'])
def order_product(id):
    user_id = auth.decode_token("user_id")
    if not user_id:
        return jsonify({"result": "fail", "message": "인증되지 않은 사용자입니다."}), 401

    post_id = ObjectId(request.form['post_id'])
    
    # 현재 상품 정보 조회
    product = db.board.find_one({'_id': post_id})
    if not product:
        return jsonify({"result": "fail", "message": "상품을 찾을 수 없습니다."}), 404

    # 구매 수량 업데이트
    amount = int(product['quantity'])
    buy_amount = int(request.form['purchase_amount'])
    update_amount = amount + buy_amount

    # 기존 participants 리스트 가져오기
    participants = product.get("participants", [])
    owner_id = product.get("ownerId")
    if user_id != owner_id and user_id not in participants:
        participants.append(user_id)

    # DB 업데이트
    result = db.board.update_one(
        {'_id': post_id},
        {"$set": {"quantity": update_amount, "participants": participants}}
    )

    if result.modified_count > 0:
        return jsonify({"result": "success", "message": "구매에 참여했습니다!"})
    else:
        return jsonify({"result": "fail", "message": "오류 발생으로 재시도 바랍니다."})