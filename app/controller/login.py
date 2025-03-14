from flask import jsonify, redirect, url_for, flash
from app.core.database import db
import jwt

@app.route('/oauth')
def oauth():
    slack_auth_url = (
        "https://slack.com/oauth/v2/authorize?"
        f"client_id={SLACK_CLIENT_ID}"
        "&scope=&user_scope=email,openid,profile"
        f"&redirect_uri={SLACK_REDIRECT_URI}"
        "&team=A08HEHGMUQL"
    )
    return redirect(slack_auth_url)


@app.route('/oauth/callback')
def oauth_callback(provider="slack"):
    # 유저가 전달한 authorization_code 수신
    code = request.args.get("code")
    if not code:
        return "Authorization failed", 400

    # Slack OAuth 서버에 Access Token 요청
    token_response = requests.post(
        "https://slack.com/api/oauth.v2.access",
        data = {
            "client_id": SLACK_CLIENT_ID,
            "client_secret": SLACK_CLIENT_SECRET,
            "code": code,
            "redirect_uri": SLACK_REDIRECT_URI,
        }
    )

    token_data = token_response.json()
    if not token_data.get("ok"):
        return "OAuth 실패", 400
    
    access_token = token_data["authed_user"]["access_token"]

    # Access Token을 통해 유저 정보 가져오기
    user_info_response = requests.get(
        "https://slack.com/api/openid.connect.userInfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_info = user_info_response.json()
    if not user_info.get("ok"):
        return "알 수 없는 유저입니다.", 400

    user = {"id": user_info.get("sub"),
            "name": user_info.get("name"), 
            "email": user_info.get("email")}
    
    # JWT token 발급
    access_token = generate_token(user, ACCESS_TOKEN_EXPIRY_DAYS)
    refresh_token = generate_token(user, REFRESH_TOKEN_EXPIRY_DAYS)

    # DB에 사용자 저장 
    users_collection.update_one(
        user,
        {"$set": {"token": refresh_token}},
        upsert=True
    )

    # 쿠키에 Access Token 저장 후 메인 페이지로 리디렉트
    response = make_response(redirect(MAIN_URL+"/index.html"))
    response.set_cookie("access_token", access_token, httponly=False, secure=True, samesite="Lax", max_age=ACCESS_TOKEN_EXPIRY_DAYS * 86400)  

    return response # 기본 엔그록 url + index.html

@app.route("/api/check-login")
def check_login():
    token = request.cookies.get("access_token")  # 쿠키에서 JWT 토큰 가져오기
    if not token:
        return jsonify({"loggedIn": False})

    try:
        jwt.decode(token, JWT_SECRET, algorithms=["HS256"])  # 토큰 검증
        return jsonify({"loggedIn": True})
    except jwt.ExpiredSignatureError:
        return jsonify({"loggedIn": False, "message": "토큰 만료"})
    except jwt.InvalidTokenError:
        return jsonify({"loggedIn": False, "message": "유효하지 않은 토큰"})

@app.route('/login.html')
def user_login():
    return render_template('login.html')

