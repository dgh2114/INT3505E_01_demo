from flask import Flask, request, jsonify
import jwt, datetime

app = Flask(__name__)

# ===== CẤU HÌNH =====
SECRET_KEY = "my_secret_key_123"        
ACCESS_TOKEN_EXPIRE_MINUTES = 0.1       
REFRESH_TOKEN_EXPIRE_DAYS = 7          

# ===== TẠO TOKEN =====
def create_access_token(user_id):
    payload = {
        "sub": user_id,
        "type": "access",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def create_refresh_token(user_id):
    payload = {
        "sub": user_id,
        "type": "refresh",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# ===== ĐĂNG NHẬP =====
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Giả lập user trong DB
    if username == "admin" and password == "123":
        access_token = create_access_token(user_id=1)
        refresh_token = create_refresh_token(user_id=1)
        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": f"{ACCESS_TOKEN_EXPIRE_MINUTES * 60} giây"
        })
    return jsonify({"error": "Sai thông tin đăng nhập"}), 401

# ===== API BẢO VỆ =====
@app.route("/profile")
def profile():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Thiếu token"}), 401

    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return jsonify({
            "message": "Truy cập hợp lệ!",
            "user_id": payload["sub"],
            "issued_at": payload["iat"],
            "expires_at": payload["exp"]
        })
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Access token đã hết hạn"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token không hợp lệ"}), 401

# ===== LÀM MỚI TOKEN =====
@app.route("/refresh", methods=["POST"])
def refresh():
    data = request.get_json()
    refresh_token = data.get("refresh_token")

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=["HS256"])
        if payload["type"] != "refresh":
            return jsonify({"error": "Không phải refresh token"}), 400

        new_access_token = create_access_token(payload["sub"])
        return jsonify({"access_token": new_access_token})
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token đã hết hạn, cần đăng nhập lại"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token không hợp lệ"}), 401

if __name__ == "__main__":
    app.run(debug=True)
