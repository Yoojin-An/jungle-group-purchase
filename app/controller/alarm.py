from datetime import datetime, timedelta, timezone
from core.database import Database as db
from flask import current_app, Blueprint
import requests

class Alarm:
    def __init__(self):
        # SLACK
        self.SLACK_CLIENT_ID = current_app.config['SLACK_CLIENT_ID']
        self.SLACK_CLIENT_SECRET = current_app.config['SLACK_CLIENT_SECRET']
        self.SLACK_REDIRECT_URI = current_app.config['SLACK_REDIRECT_URI']
        self.SLACK_TOKEN = current_app.config['SLACK_TOKEN']

        # JWT
        self.JWT_SECRET = current_app.config['JWT_SECRET']
        self.ACCESS_TOKEN_EXPIRY_DAYS = current_app.config['ACCESS_TOKEN_EXPIRY_DAYS']
        self.REFRESH_TOKEN_EXPIRY_DAYS = current_app.config['REFRESH_TOKEN_EXPIRY_DAYS']

    '''마감일이 지난 상품 검색 -> 해당 메서드는 APScheduler를 통해 실행'''
    def check_expired_products(self):
        """ 공동구매 마감된 게시글 찾고 상태 업데이트 """
        now = datetime.now().strftime("%Y-%m-%d")  # 날짜를 "YYYY-MM-DD" 형식의 문자열로 변환
        
        # 마감 기한이 지난 게시글 조회
        expired_products = db.find({
            "deadline": {"$lt": now},  # 문자열 비교
            "expired": {"$ne": True}
        })
        
        for product in expired_products:
            self.send_messageToparticipants(product)
            self.send_messageToOwner(product)
            self.db.update_one(
                {"_id": product["_id"]},
                {"$set": {"expired": True}}
            )

    ''' 구매 희망 유저들에게 슬랙 디엠 전송 기능 '''
    def send_messageToparticipants(self, product):
        message = product['message']
        participants = product['participants']

        for userId in participants:
            data = {
                'token' : self.SLACK_TOKEN,
                'channel' : userId,
                'as_user' : True,
                'text' : message
            }
            requests.post(
                url='https://slack.com/api/chat.postMessage',
                data=data)

    ''' 상품 게시글 게시자에게 슬랙 디엠 전송 기능 '''
    def send_messageToOwner(self, product):
        total_quantity = product['quantity']
        total_price = int(product['price']) * int(product['quantity'])
        ownerId = product['ownerId']

        data = {
                'token' : self.SLACK_TOKEN,
                'channel' : ownerId,
                'as_user' : True,
                'text' : f"총 구매 금액은 {total_price}, 총 수량은 {total_quantity}"
        }
        
        requests.post(
                url='https://slack.com/api/chat.postMessage',
                data=data)