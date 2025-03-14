from flask import Flask, render_template, jsonify, request, redirect, make_response, session
import requests
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler
import jwt
from functools import wraps
from bson.objectid import ObjectId
from flask_cors import CORS
import threading

app = Flask(__name__)

CORS(app, supports_credentials=True)



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index.html', methods=['GET'])
def getMainPage():
    return render_template('index.html')

@app.route('/create-product.html', methods=['GET'])
def getCreateProduct():
    return render_template('create-product.html')

@app.route('/login.html')
def user_login():
    return render_template('login.html')

