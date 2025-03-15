import os
from flask import Flask
from app.core.database import Database
from app.core.auth import Auth
from dotenv import load_dotenv

from app.controller.login import router as login_router
from app.controller.board import router as board_router
from app.controller.post import router as post_router
from app.controller.comment import router as comment_router
from app.controller.order import router as order_router

auth = None
db = None

def create_app(config=None):
    global auth, db

    if auth is None:
        auth = Auth()
    if db is None:
        db = Database()

    load_dotenv()

    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    app = Flask(__name__, template_dir)

    app.config['MAIN_URL'] = 'https://43.201.98.116.nip.io'
    app.config['SLACK_REDIRECT_URI'] = 'https://43.201.98.116.nip.io/oauth/callback'
    app.config['SLACK_CLIENT_ID'] = os.getenv('SLACK_CLIENT_ID')
    app.config['SLACK_CLIENT_SECRET'] = os.getenv('SLACK_CLIENT_SECRET')
    app.config['SLACK_TOKEN'] = os.getenv('SLACK_TOKEN')
    app.config['JWT_SECRET'] = os.getenv('JWT_SECRET')
    app.config['JWT_ALGORITHM'] = 'HS256'
    app.config['ACCESS_TOKEN_EXPIRY_DAYS'] = 0.5
    app.config['REFRESH_TOKEN_EXPIRY_DAYS'] = 150

    app.register_blueprint(login_router)
    app.register_blueprint(board_router)
    app.register_blueprint(post_router)
    app.register_blueprint(comment_router)
    app.register_blueprint(order_router)

    return app