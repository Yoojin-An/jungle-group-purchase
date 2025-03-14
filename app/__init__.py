import os
from flask import Flask
from app.core.database import init_db
from app.core.extension import init_extensions, jwt
from jinja2 import Environment

def create_app(config=None):
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    app = Flask(__name__, template_dir)
    app.config['MAIN_URL'] = 'https://43.201.98.116.nip.io'
    app.config['SLACK_CLIENT_ID'] = ''
    app.config['SLACK_CLIENT_SECRET'] = ''
    app.config['SLACK_REDIRECT_URI'] = 'https://43.201.98.116.nip.io/oauth'
    app.config['SLACK_TOKEN'] =  ''
    app.config['JWT_SECRET'] = ''
    app.config['JWT_ALGORITHM'] = 'HS256'
    app.config['ACCESS_TOKEN_EXPIRY_DAYS'] = 0.5 
    app.config['REFRESH_TOKEN_EXPIRY_DAYS'] = 150