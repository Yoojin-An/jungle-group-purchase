from flask import app, render_template
from core.database import Database as db

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index.html', methods=['GET'])
def getMainPage():
    return render_template('index.html')

@app.route('/board', methods=['GET'])
def read_all_posts():
    check_ship_condition()
    result = list(db.posts.find({}))
    
    formatted_posts = [
        {   
            "id": str(post["_id"]),
            "title": post["board"],
            "price": f"{post['price']}원",
            "deadline": post["deadline"],
            "category": post["category"],
            "condition": post["condition"]
        }
        for post in result
    ]

    return jsonify({'result':'success', 'products': formatted_posts})

def check_ship_condition():
    result = list(db.posts.find({}))

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
