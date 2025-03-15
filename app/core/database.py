from pymongo import MongoClient

class Database:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.collection = client.board