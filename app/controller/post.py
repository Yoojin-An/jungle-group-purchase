import request
from flask import Blueprint, render_template, jsonify, router
from bson.objectid import ObjectId
from core.database import Database as db
from core.auth import Auth as auth

# @app.route('/product/<id>', methods=["GET"])
# def find_product(id):
#     product_id = ObjectId(id)  # 유효한 ObjectId로 변환
#     product = db.boards.find_one({"_id": product_id})

#     product["_id"] = str(product["_id"])  # _id를 문자열로 변환하여 반환
#     return jsonify({"result": "success", "product": product})

router = Blueprint("comment", __name__, url_prefix="/post")

@router.route('/<id>', methods=['GET'])
def find_post(id):
    product = db.find_one({"_id": ObjectId(id)})
    if product:
        return render_template('product.html', product=product)
    else:
        return jsonify({"result": "fail", "message": "상품을 찾을 수 없습니다."}), 404

@router.route('/', methods=['POST'])
@auth.jwt_required
def create_post():
    userId = auth.decode_token("userId")
    if not userId:
        return jsonify({'error': 'Invalid or missing token'}), 401

    title = request.form['title']
    name = request.form['item_name']
    link = request.form['item_url']
    price = request.form['item_price']
    deadline = request.form['deadline']
    shipping = request.form['delivery_fee']
    condition = "N"
    message = request.form['confirmation_msg']
    category = request.form['category']
    quantity = request.form['item_count']
    ownerId = userId

    post = { 'board': title, 'name':name, 'link':link, 'price':price, 
            'deadline':deadline, 'shipping':shipping, 'condition':condition, 
            'message':message, 'category':category, 'quantity':quantity, 
            'ownerId' : ownerId , 'participants': [], "expired": False}
    
    db.boards.insert_one(post)
    # return jsonify({'result': 'success'})
    return render_template('post.html')

@router.route('/', methods=['POST']) 
@auth.jwt_required
def update_post():
    post_id = ObjectId(request.form['post_id']) 
    update_boards = request.form['update_boards']
    update_name = request.form['update_name']
    update_link = request.form['update_link']
    update_price = request.form['update_price']
    update_deadline = request.form['update_deadline']
    update_shipping = request.form['update_shipping']
    update_condition = request.form['update_condition']
    update_category = request.form['update_category']
    result = db.boards.update_one(
        {"_id": post_id},
        {"$set": {
            "board": update_boards,
            "name": update_name,
            "link": update_link,
            "price": update_price ,
            "deadline": update_deadline,
            "shipping": update_shipping,
            "condition": update_condition,
            "category": update_category }}
    )
    if result.modified_count > 0:
        return jsonify({"result": "success", "message": "수정되었습니다!"})
    else:
        return jsonify({"result": "fail", "message": "오류 발생으로 재시도 바랍니다."})
