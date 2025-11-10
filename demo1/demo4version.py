from flask import Flask, jsonify, request, make_response
import hashlib

app = Flask(__name__)

# ===============================
# Fake resource data
# ===============================
books = [
    {"id": 1, "title": "SOA - Kien truc huong dich vu", "available": True},
    {"id": 2, "title": "Thu vien muon - tra sach", "available": False},
]

news_article = {
    "id": 1,
    "title": "RESTful API la gi?",
    "content": "RESTful la mot kien truc giup xay dung web service linh hoat va de mo rong."
}

# ============================================================
# 1️⃣ CLIENT–SERVER
# Tach biet phan giao dien (client) va xu ly (server).
# Client chi can goi API de lay du lieu JSON.
# ============================================================
@app.route('/books', methods=['GET'])
def get_books():
    return jsonify({
        "message": "Lay danh sach sach thanh cong",
        "data": books
    }), 200


# ============================================================
# 2️⃣ STATELESS
# Server khong luu trang thai nguoi dung.
# Moi request phai tu mang du thong tin xac thuc (vd: token).
# ============================================================
@app.route('/borrow/<int:book_id>', methods=['POST'])
def borrow_book(book_id):
    token = request.headers.get("Authorization")

    # Moi request deu phai co token -> minh hoa tinh Stateless
    if token != "Bearer admin-token":
        return jsonify({"error": "Thieu hoac sai token xac thuc"}), 401

    for b in books:
        if b["id"] == book_id:
            if not b["available"]:
                return jsonify({"error": "Sach nay da duoc muon"}), 400
            b["available"] = False
            return jsonify({"message": f"Da muon '{b['title']}' thanh cong"}), 200
    return jsonify({"error": "Khong tim thay sach"}), 404


# ============================================================
# 3️⃣ CACHEABLE (ket hop Cache-Control va ETag)
# Cho phep client luu cache va kiem tra thay doi bang ETag.
# ============================================================
@app.route('/news', methods=['GET'])
def get_news():
    # Tao ETag tu hash noi dung bai viet
    etag = hashlib.sha1(str(news_article).encode()).hexdigest()

    # Kiem tra neu client gui If-None-Match
    client_etag = request.headers.get("If-None-Match")
    if client_etag == etag:
        # Du lieu chua thay doi -> 304 Not Modified
        return '', 304

    # Gui du lieu moi kem ETag va Cache-Control
    resp = make_response(jsonify(news_article))
    resp.headers["ETag"] = etag
    resp.headers["Cache-Control"] = "public, max-age=120"  # cache 2 phut
    return resp


# ============================================================
# 4️⃣ UNIFORM INTERFACE
# Giao dien thong nhat: tat ca tai nguyen dung cung pattern:
#   GET /books, POST /books, PUT /books/<id>, DELETE /books/<id>
# ============================================================

# Them moi
@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "Thieu thong tin sach"}), 400
    new_book = {
        "id": len(books) + 1,
        "title": data["title"],
        "available": True
    }
    books.append(new_book)
    return jsonify({"message": "Them sach thanh cong", "book": new_book}), 201


# Cap nhat
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
    for b in books:
        if b["id"] == book_id:
            b.update(data)
            return jsonify({"message": "Cap nhat thanh cong", "book": b}), 200
    return jsonify({"error": "Khong tim thay sach"}), 404


# Xoa
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    books = [b for b in books if b["id"] != book_id]
    return '', 204


# ============================================================
# Xu ly loi 404 (Uniform Interface nhat quan)
# ============================================================
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Duong dan khong ton tai"}), 404


if __name__ == '__main__':
    app.run(debug=True)
