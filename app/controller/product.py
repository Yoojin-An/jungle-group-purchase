

@app.route('/create-product.html', methods=['GET'])
def getCreateProduct():
    return render_template('create-product.html')

'''특정 게시물 페이지 '''
@app.route('/product-detail/<id>', methods=['GET'])
def product_detail(id):
    print('here', id)
    product = db.boards.find_one({"_id": ObjectId(id)})
    if product:
        return render_template('product-detail.html', product=product)
    else:
        return jsonify({"result": "fail", "message": "상품을 찾을 수 없습니다."}), 404

'''특정 상품 정보 조회'''
@app.route('/find_product/<id>', methods=["GET"])
def find_product(id):
        product_id = ObjectId(id)  # 유효한 ObjectId로 변환
        product = db.boards.find_one({"_id": product_id})

        product["_id"] = str(product["_id"])  # _id를 문자열로 변환하여 반환
        return jsonify({"result": "success", "product": product})


''' 모든 상품 게시글 조회'''
@app.route('/api/products', methods=['GET'])
def getAllProducts():
    check_ship_condition()
    result = list(db.boards.find({}))
    
    formatted_products = [
        {   
            "id": str(product["_id"]),
            "title": product["board"],  # 'name' 필드를 'title'로 변경
            "price": f"{product['price']}원",  # 가격에 "원" 추가
            "deadline": product["deadline"],  # 날짜 형식 그대로 사용
            "category": product["category"],
            "condition": product["condition"]
        }
        for product in result
    ]

    return jsonify({'result':'success', 'products': formatted_products})



'''상품 게시글 생성'''

@app.route('/api/product', methods=['POST'])
@jwt_required
def createProduct():
    userId = decode_token()
    print("!!!!!!here!!!!!!!", userId)
    if not userId:
        return jsonify({'error': 'Invalid or missing token'}), 401


    board = request.form['title']
    name = request.form['item_name']
    link = request.form['item_url']
    price = request.form['item_price']
    deadline = request.form['deadline'] # 2025-03-03, YYYY-MM-DD
    shipping = request.form['delivery_fee']
    condition = "N"
    #condition = request.form['free_delivery_cond']
    message = request.form['confirmation_msg']
    category = request.form['category']
    quantity = request.form['item_count']
    ownerId = userId

    product = { 'board': board, 'name':name, 'link':link, 'price':price, 
                'deadline':deadline, 'shipping':shipping, 'condition':condition, 
                'message':message, 'category':category, 'quantity':quantity, 
                'ownerId' : ownerId , 'participants': [], "expired": False}
    
    db.boards.insert_one(product)
    return jsonify({'result': 'success'})



def check_ship_condition():
    result = list(db.boards.find({}))

    for product in result:
        price = product['price']
        quantity = product['quantity']
        shipping = product['shipping']
        
        # price * quantity가 shipping보다 크면 condition을 "Y"로 업데이트
        if int(price) * int(quantity) >= int(shipping):
            db.boards.update_one(
                {'_id': product['_id']},
                {'$set': {'condition': 'Y'}}
            )
        else:
            # 기본값을 "N"으로 설정
            db.boards.update_one(
                {'_id': product['_id']},
                {'$set': {'condition': 'N'}})

@app.route('/buy_product/<id>', methods=['POST'])
def buy_product(id):
    user_id = decode_token()  # 토큰에서 user_id 가져오기
    if not user_id:
        return jsonify({"result": "fail", "message": "인증되지 않은 사용자입니다."}), 401

    post_id = ObjectId(request.form['post_id'])
    
    # 현재 상품 정보 조회
    product = db.boards.find_one({'_id': post_id})
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
        participants.append(user_id)    # user_id 추가

    # DB 업데이트
    result = db.boards.update_one(
        {'_id': post_id},
        {"$set": {"quantity": update_amount, "participants": participants}}
    )

    if result.modified_count > 0:
        return jsonify({"result": "success", "message": "구매에 참여했습니다!!!"})
    else:
        return jsonify({"result": "fail", "message": "오류 발생으로 재시도 바랍니다."})

@app.route('/update_post', methods=['POST']) 
def Update_post():
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
        return jsonify({"result": "success", "message": "수정되었습니다다!!!"})
    else:
        return jsonify({"result": "fail", "message": "오류 발생으로 재시도 바랍니다."})



