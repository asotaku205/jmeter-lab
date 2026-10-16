"""Demo Shop API - ung dung minh hoa lam muc tieu kiem thu hieu nang bang JMeter."""
import random
import time
from flask import Flask, jsonify, request

app = Flask(__name__)

PRODUCTS = [
    {"id": 1, "name": "Laptop Pro 14", "price": 28990000, "stock": 15},
    {"id": 2, "name": "Chuot khong day", "price": 450000, "stock": 120},
    {"id": 3, "name": "Ban phim co", "price": 1290000, "stock": 60},
    {"id": 4, "name": "Man hinh 27 inch 2K", "price": 6990000, "stock": 25},
    {"id": 5, "name": "Tai nghe bluetooth", "price": 1590000, "stock": 80},
    {"id": 6, "name": "O cung SSD 1TB", "price": 2190000, "stock": 45},
    {"id": 7, "name": "Webcam Full HD", "price": 890000, "stock": 30},
    {"id": 8, "name": "Loa mini", "price": 650000, "stock": 50},
]

USERS = {f"user{i:02d}": "pass123" for i in range(1, 11)}


@app.route("/")
def home():
    return (
        "<html><head><title>Demo Shop</title></head>"
        "<body><h1>Demo Shop - Trang chu</h1>"
        "<p>Chao mung den voi cua hang demo phuc vu kiem thu hieu nang JMeter.</p>"
        "</body></html>"
    )


@app.route("/api/products")
def list_products():
    time.sleep(random.uniform(0.02, 0.08))  # mo phong do tre xu ly
    return jsonify(PRODUCTS)


@app.route("/api/products/<int:pid>")
def product_detail(pid):
    time.sleep(random.uniform(0.01, 0.05))
    product = next((p for p in PRODUCTS if p["id"] == pid), None)
    if product is None:
        return jsonify({"error": "San pham khong ton tai"}), 404
    return jsonify(product)


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username", "")
    if USERS.get(username) == data.get("password"):
        return jsonify({"token": f"demo-token-{username}", "username": username})
    return jsonify({"error": "Sai ten dang nhap hoac mat khau"}), 401


@app.route("/api/orders")
def orders():
    time.sleep(random.uniform(0.02, 0.06))
    username = request.args.get("user", "guest")
    return jsonify(
        [
            {
                "order_id": f"DH-{username}-001",
                "user": username,
                "total": 1290000,
                "status": "da_giao",
            },
            {
                "order_id": f"DH-{username}-002",
                "user": username,
                "total": 450000,
                "status": "dang_giao",
            },
        ]
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, threaded=True)
