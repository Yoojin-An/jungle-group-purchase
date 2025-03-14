from functools import wraps

from flask import jsonify

def jwt_required(func):
    @wraps(func)
    def authenticated_function(*args, **kwargs):
        token = request.cookies.get("access_token")

        if not token:
            return jsonify({"error": "Authentication required"}), 401

        try:
            # JWT 토큰을 검증하고 해석
            jwt.decode(token, key=JWT_SECRET, algorithms=["HS256"])

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Access Token이 만료되었습니다."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Access Token 형식이 유효하지 않습니다."}), 401

        return func(*args, **kwargs)

    return authenticated_function

def generate_token(user, token_expiry_days):
    payload = {
        "user_id": user.get("id"),
        "name": user.get("name"),
        "email": user.get("email"),
        "exp": (datetime.now(timezone.utc) + timedelta(days=token_expiry_days)).timestamp(),
    }

    return jwt.encode(payload=payload, key=JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None  # 유효하지 않은 토큰

    token = auth_header.split(" ")[1]  # "Bearer TOKEN"에서 TOKEN 추출
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])  # 토큰 검증 및 디코딩
        return payload.get("user_id")  # 토큰에서 userId 추출
    except jwt.ExpiredSignatureError:
        return None  # 토큰 만료
    except jwt.InvalidTokenError:
        return None  # 유효하지 않은 토큰

def decode_name():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None  # 유효하지 않은 토큰

    token = auth_header.split(" ")[1]  # "Bearer TOKEN"에서 TOKEN 추출
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])  # 토큰 검증 및 디코딩
        return payload.get("name")  # 토큰에서 name 추출
    except jwt.ExpiredSignatureError:
        return None  # 토큰 만료
    except jwt.InvalidTokenError:
        return None  # 유효하지 않은 토큰