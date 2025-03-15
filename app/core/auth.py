import request
import jwt
from functools import wraps
from flask import jsonify, current_app
from datetime import datetime, timedelta, timezone

class Auth:
    def __init__(self):
        self.JWT_SECRET = current_app.config['JWT_SECRET']
        self.JWT_ALGORITHM = current_app.config['JWT_ALGORITHM']

    def jwt_required(self, func):
        @wraps(func)
        def authenticated_function(*args, **kwargs):
            token = request.cookies.get("access_token")

            if not token:
                return jsonify({"error": "유효하지 않은 접근입니다."}), 401

            try:
                # JWT 토큰을 검증하고 해석
                jwt.decode(token, key=self.JWT_SECRET, algorithms=self.JWT_ALGORITHM)

            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Access Token이 만료되었습니다."}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Access Token 형식이 유효하지 않습니다."}), 401

            return func(*args, **kwargs)

        return authenticated_function

    def generate_token(self, user, token_expiry_days):
        payload = {
            "user_id": user.get("id"),
            "name": user.get("name"),
            "email": user.get("email"),
            "exp": (datetime.now(timezone.utc) + timedelta(days=token_expiry_days)).timestamp(),
        }

        return jwt.encode(payload=payload, key=self.JWT_SECRET, algorithm=self.JWT_ALGORITHM)

    def decode_token(self, claim):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None  # 유효하지 않은 토큰

        token = auth_header.split(" ")[1]  # "Bearer TOKEN"에서 TOKEN 추출
        try:
            payload = jwt.decode(token, self.JWT_SECRET, algorithms=self.JWT_ALGORITHM)  # 토큰 검증 및 디코딩
            return payload.get(claim)  # 토큰에서 원하는 claim 추출
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return jsonify({"error": "유효하지 않은 접근입니다."}), 401