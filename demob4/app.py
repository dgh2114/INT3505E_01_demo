from flask import Flask, jsonify, request, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
import jwt, datetime, os

app = Flask(__name__)
app.config["SECRET_KEY"] = "MY_SUPER_SECRET_KEY"

# ==========================================
# 📚 Dữ liệu mẫu (Stateless)
# ==========================================
books = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin"},
    {"id": 2, "title": "The Pragmatic Programmer", "author": "Andy Hunt"},
]

# ==========================================
# 🔐 Authentication Endpoint
# ==========================================
@app.route("/auth/token", methods=["POST"])
def get_token():
    """Nhận username, password và trả về JWT token"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Demo: xác thực cứng
    if username == "admin" and password == "123":
        token = jwt.encode({
            "user": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, app.config["SECRET_KEY"], algorithm="HS256")
        return jsonify({"access_token": token})
    else:
        return jsonify({"error": "Invalid credentials"}), 401


# ==========================================
# 🧩 Middleware kiểm tra JWT
# ==========================================
def require_token(func):
    """Decorator để kiểm tra JWT"""
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401
        token = auth_header.split(" ")[1]
        try:
            jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


# ==========================================
# 📖 CRUD API (Stateless)
# ==========================================
@app.route("/api/books", methods=["GET"])
@require_token
def get_books():
    return jsonify(books)

@app.route("/api/books/<int:book_id>", methods=["GET"])
@require_token
def get_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book)

@app.route("/api/books", methods=["POST"])
@require_token
def add_book():
    data = request.get_json()
    new_book = {
        "id": len(books) + 1,
        "title": data["title"],
        "author": data["author"]
    }
    books.append(new_book)
    return jsonify(new_book), 201

@app.route("/api/books/<int:book_id>", methods=["PUT"])
@require_token
def update_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    data = request.get_json()
    book.update(data)
    return jsonify(book)

@app.route("/api/books/<int:book_id>", methods=["DELETE"])
@require_token
def delete_book(book_id):
    global books
    books = [b for b in books if b["id"] != book_id]
    return jsonify({"message": "Book deleted"}), 200


# ==========================================
# 📘 Serve file openapi.yaml ở cùng cấp app.py
# ==========================================
@app.route("/openapi.yaml")
def openapi_yaml():
    path = os.path.dirname(__file__)
    print(">>> DEBUG: Flask đang gửi file openapi.yaml từ:", path)
    print(">>> DEBUG: Danh sách file:", os.listdir(path))
    return send_from_directory(path, "openapi.yaml")


# ==========================================
# 🧭 Swagger UI
# ==========================================
SWAGGER_URL = "/docs"
API_URL = "/openapi.yaml"  # đúng đường dẫn YAML
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Book Management API (Swagger Demo)"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

print(">>> File app.py đang được thực thi!")

# ==========================================
# 🚀 Run App
# ==========================================
if __name__ == "__main__":
    app.run(debug=True)
