from flask import Flask, jsonify, request, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
import jwt, datetime, os, functools

app = Flask(__name__)
app.config["SECRET_KEY"] = "MY_SUPER_SECRET_KEY"

# ==========================================
# Dữ liệu mẫu (nhiều sách hơn)
# ==========================================
books = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin"},
    {"id": 2, "title": "The Pragmatic Programmer", "author": "Andy Hunt"},
    {"id": 3, "title": "Refactoring", "author": "Martin Fowler"},
    {"id": 4, "title": "Design Patterns", "author": "Erich Gamma"},
    {"id": 5, "title": "Code Complete", "author": "Steve McConnell"},
]

# ==========================================
# Authentication Endpoint
# ==========================================
@app.route("/auth/token", methods=["POST"])
def get_token():
    """Đăng nhập -> trả về access token có thời hạn"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")

    if (username, password) in [("admin", "123"), ("user", "123")]:
        token = jwt.encode({
            "user": username,
            "role": role,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=60),
            "iat": datetime.datetime.utcnow()
        }, app.config["SECRET_KEY"], algorithm="HS256")

        return jsonify({
            "access_token": token,
            "expires_in": "60 giây",
            "role": role,
            "note": "Token sống 60s. Admin có thể thêm, sửa, xem chi tiết hoặc xóa sách."
        })
    return jsonify({"error": "Sai username hoặc password"}), 401


# ==========================================
# Middleware kiểm tra JWT
# ==========================================
def require_token(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Thiếu hoặc sai định dạng token"}), 401
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Access token đã hết hạn"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token không hợp lệ"}), 401
        return func(*args, **kwargs)
    return wrapper


# ==========================================
# Middleware kiểm tra quyền (role)
# ==========================================
def require_role(role):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if request.user.get("role") != role:
                return jsonify({"error": f"Chỉ {role.upper()} mới được phép thực hiện hành động này"}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ==========================================
# CRUD API
# ==========================================
@app.route("/api/books", methods=["GET"])
@require_token
def get_books():
    """Lấy danh sách tất cả sách"""
    return jsonify({
        "books": books,
        "total": len(books),
        "current_user": request.user["user"],
        "role": request.user["role"]
    })


@app.route("/api/books/<int:book_id>", methods=["GET"])
@require_token
@require_role("admin")
def get_book(book_id):
    """Admin xem chi tiết 1 sách cụ thể"""
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "Không tìm thấy sách"}), 404
    return jsonify({"book": book})


@app.route("/api/books", methods=["POST"])
@require_token
@require_role("admin")
def add_book():
    """Thêm sách mới"""
    data = request.get_json()
    if not data or "title" not in data or "author" not in data:
        return jsonify({"error": "Thiếu thông tin (title, author)"}), 400
    new_id = max(b["id"] for b in books) + 1 if books else 1
    new_book = {"id": new_id, "title": data["title"], "author": data["author"]}
    books.append(new_book)
    return jsonify({"message": "Đã thêm sách mới", "book": new_book}), 201


@app.route("/api/books/<int:book_id>", methods=["PUT"])
@require_token
@require_role("admin")
def update_book(book_id):
    """Sửa thông tin sách"""
    data = request.get_json()
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "Không tìm thấy sách"}), 404
    book.update({
        "title": data.get("title", book["title"]),
        "author": data.get("author", book["author"])
    })
    return jsonify({"message": "Cập nhật thành công", "book": book}), 200


@app.route("/api/books/<int:book_id>", methods=["DELETE"])
@require_token
@require_role("admin")
def delete_book(book_id):
    """Xóa sách"""
    global books
    before_count = len(books)
    books = [b for b in books if b["id"] != book_id]
    if len(books) == before_count:
        return jsonify({"error": "Không tìm thấy sách"}), 404
    return jsonify({"message": f"Đã xóa sách có id {book_id}"}), 200


# ==========================================
# Swagger UI
# ==========================================
@app.route("/openapi.yaml")
def openapi_yaml():
    path = os.path.dirname(__file__)
    return send_from_directory(path, "openapi.yaml")

SWAGGER_URL = "/docs"
API_URL = "/openapi.yaml"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL,
    config={"app_name": "Book Management API – Full CRUD Demo"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == "__main__":
    app.run(debug=True)
