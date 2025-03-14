from pymongo import MongoClient

def init_db():
    client = MongoClient('localhost', 27017)
    db = client.boards
    users_collection = db.users
    tokens_collection = db.tokens