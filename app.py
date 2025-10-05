from flask import Flask, jsonify, redirect, request

app = Flask(__name__)

# Giả lập dữ liệu sách
books = [
    {"id": 1, "title": "SOA - Kien truc huong dich vu", "available": True},
    {"id": 2, "title": "Thu vien muon - tra sach", "available": False},
]

# 200 OK – Lấy danh sách sách thành công
@app.route('/books', methods=['GET'])
def get_books():
    return jsonify({"message": "Lay danh sach thanh cong", "data": books}), 200


# 201 Created – Thêm sách mới
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


# 204 No Content – Xóa sách (không trả về nội dung)
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    for b in books:
        if b["id"] == book_id:
            books.remove(b)
            return '', 204  # Không trả về nội dung nào
    return jsonify({"error": "Khong tim thay sach"}), 404


# 301 Moved Permanently – Chuyển hướng sang trang mới
@app.route('/old-books')
def old_books():
    return redirect("/books", code=301)


# 403 Forbidden – Người dùng không có quyền mượn sách
@app.route('/borrow/<int:book_id>', methods=['POST'])
def borrow_book(book_id):
    user_role = request.args.get("role", "guest")
    if user_role != "member":
        return jsonify({"error": "Bạn khong co quyen muon sach (chi thanh vien moi duoc phep)."}), 403
    for b in books:
        if b["id"] == book_id:
            if not b["available"]:
                return jsonify({"error": "Sach nay da duoc muon."}), 400
            b["available"] = False
            return jsonify({"message": f"Ban da muon '{b['title']}' thanh cong."}), 200
    return jsonify({"error": "Khong tim thay sach"}), 404


# 404 Not Found – Đường dẫn không tồn tại
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Duong dan khong ton tai"}), 404


# 500 Internal Server Error – Lỗi hệ thống giả lập
@app.route('/error')
def error_demo():
    try:
        x = 1 / 0  # Gây lỗi chia 0
    except Exception as e:
        return jsonify({"error": "Loi he thong noi bo", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
