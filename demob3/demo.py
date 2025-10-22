from flask import Flask, jsonify, request

app = Flask(__name__)

# =============================
# Version 1 (v1)
# =============================
# V1 có nhiều trường chi tiết như 'age', 'address', 'phone'
users_v1 = [
    {"id": 1, "name": "Alice", "age": 25, "address": "Hanoi", "phone": "0123-456-789"},
    {"id": 2, "name": "Bob", "age": 30, "address": "HCM", "phone": "0987-654-321"},
]

@app.route('/api/v1/users', methods=['GET'])
def get_users_v1():
    return jsonify({
        "version": "v1",
        "description": "Phiên bản cũ - có đầy đủ thông tin cá nhân",
        "data": users_v1
    }), 200


# =============================
# Version 2 (v2)
# =============================
# V2 thay đổi:
# - Bỏ các trường 'age', 'phone'
# - Giữ 'id', 'name', 'address'
#   Thêm 'role' mới
# => Minh họa API version có thể *loại bỏ hoặc tái cấu trúc* dữ liệu
users_v2 = [
    {"id": 1, "name": "Alice", "address": "Hanoi", "role": "admin"},
    {"id": 2, "name": "Bob", "address": "HCM", "role": "user"},
]

@app.route('/api/v2/users', methods=['GET'])
def get_users_v2():
    return jsonify({
        "version": "v2",
        "description": "Phiên bản mới - ẩn bớt thông tin cá nhân, thêm role",
        "data": users_v2
    }), 200


# =============================
# Version Comparison Endpoint
# =============================
@app.route('/api/compare', methods=['GET'])
def compare_versions():
    """So sánh các trường khác biệt giữa v1 và v2"""
    v1_fields = set(users_v1[0].keys())
    v2_fields = set(users_v2[0].keys())

    removed = v1_fields - v2_fields
    added = v2_fields - v1_fields
    common = v1_fields & v2_fields

    return jsonify({
        "v1_fields": list(v1_fields),
        "v2_fields": list(v2_fields),
        "removed_fields_in_v2": list(removed),
        "added_fields_in_v2": list(added),
        "common_fields": list(common)
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
