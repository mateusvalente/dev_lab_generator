import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import oracledb

app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
    expose_headers=["Content-Type"],
)
DB_CLIENT = os.getenv("DB_CLIENT", "mysql").lower()


def get_conn():
    if DB_CLIENT == "oracle":
        return oracledb.connect(
            user=os.getenv("DB_USER", "LABUSER"),
            password=os.getenv("DB_PASSWORD", "labpass"),
            dsn=f"{os.getenv('DB_HOST', 'db')}:{os.getenv('DB_PORT', '1521')}/{os.getenv('DB_NAME', 'FREEPDB1')}",
        )
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "db"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "labuser"),
        password=os.getenv("DB_PASSWORD", "labpass"),
        database=os.getenv("DB_NAME", "labdb"),
        charset="utf8mb4",
        collation="utf8mb4_unicode_ci",
    )


def upper_case_keys(data):
    if isinstance(data, list):
        return [upper_case_keys(item) for item in data]
    if isinstance(data, dict):
        return {str(key).upper(): upper_case_keys(value) for key, value in data.items()}
    return data


def body_value(data, field, default=None):
    return data.get(field, data.get(field.upper(), default))


def row_to_dict(cursor, row):
    columns = [description[0].upper() for description in cursor.description] if cursor.description else []
    return dict(zip(columns, row))


@app.get("/api/health")
def healthcheck():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS TOTAL FROM categories")
    categories = int(cur.fetchone()[0])
    cur.close()
    conn.close()
    return jsonify({"STATUS": "ok", "DB_CLIENT": DB_CLIENT, "CATEGORIES": categories})


@app.get("/api/categories")
def list_categories():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, description FROM categories ORDER BY id")
    rows = [row_to_dict(cur, row) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(rows)


@app.get("/api/categories/<int:item_id>")
def get_category(item_id):
    conn = get_conn()
    cur = conn.cursor()
    sql = "SELECT id, name, description FROM categories WHERE id = :1" if DB_CLIENT == "oracle" else "SELECT id, name, description FROM categories WHERE id = %s"
    cur.execute(sql, [item_id])
    row = cur.fetchone()
    payload = row_to_dict(cur, row) if row else None
    cur.close()
    conn.close()
    return (jsonify(payload), 200) if payload else (jsonify({"ERROR": "Not found"}), 404)


@app.post("/api/categories")
def create_category():
    data = request.get_json(force=True) or {}
    name = body_value(data, "name", "")
    description = body_value(data, "description")
    conn = get_conn()
    cur = conn.cursor()
    sql = "INSERT INTO categories(name, description) VALUES (:1, :2)" if DB_CLIENT == "oracle" else "INSERT INTO categories(name, description) VALUES (%s, %s)"
    cur.execute(sql, [name, description])
    conn.commit()
    cur.execute("SELECT MAX(id) AS ID FROM categories")
    item_id = int(cur.fetchone()[0])
    cur.close()
    conn.close()
    return jsonify({"ID": item_id}), 201


@app.put("/api/categories/<int:item_id>")
def update_category(item_id):
    data = request.get_json(force=True) or {}
    name = body_value(data, "name", "")
    description = body_value(data, "description")
    conn = get_conn()
    cur = conn.cursor()
    sql = "UPDATE categories SET name = :1, description = :2 WHERE id = :3" if DB_CLIENT == "oracle" else "UPDATE categories SET name = %s, description = %s WHERE id = %s"
    cur.execute(sql, [name, description, item_id])
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"UPDATED": True})


@app.delete("/api/categories/<int:item_id>")
def delete_category(item_id):
    conn = get_conn()
    cur = conn.cursor()
    sql = "DELETE FROM categories WHERE id = :1" if DB_CLIENT == "oracle" else "DELETE FROM categories WHERE id = %s"
    cur.execute(sql, [item_id])
    conn.commit()
    cur.close()
    conn.close()
    return ("", 204)


@app.get("/api/products")
def list_products():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT p.id, p.category_id, p.name, p.price, p.stock, c.name AS category_name FROM products p JOIN categories c ON c.id = p.category_id ORDER BY p.id")
    rows = [row_to_dict(cur, row) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(rows)


@app.get("/api/products/<int:item_id>")
def get_product(item_id):
    conn = get_conn()
    cur = conn.cursor()
    sql = "SELECT id, category_id, name, price, stock FROM products WHERE id = :1" if DB_CLIENT == "oracle" else "SELECT id, category_id, name, price, stock FROM products WHERE id = %s"
    cur.execute(sql, [item_id])
    row = cur.fetchone()
    payload = row_to_dict(cur, row) if row else None
    cur.close()
    conn.close()
    return (jsonify(payload), 200) if payload else (jsonify({"ERROR": "Not found"}), 404)


@app.post("/api/products")
def create_product():
    data = request.get_json(force=True) or {}
    category_id = body_value(data, "category_id", 0)
    name = body_value(data, "name", "")
    price = body_value(data, "price", 0)
    stock = body_value(data, "stock", 0)
    conn = get_conn()
    cur = conn.cursor()
    sql = "INSERT INTO products(category_id, name, price, stock) VALUES (:1, :2, :3, :4)" if DB_CLIENT == "oracle" else "INSERT INTO products(category_id, name, price, stock) VALUES (%s, %s, %s, %s)"
    cur.execute(sql, [category_id, name, price, stock])
    conn.commit()
    cur.execute("SELECT MAX(id) AS ID FROM products")
    item_id = int(cur.fetchone()[0])
    cur.close()
    conn.close()
    return jsonify({"ID": item_id}), 201


@app.put("/api/products/<int:item_id>")
def update_product(item_id):
    data = request.get_json(force=True) or {}
    category_id = body_value(data, "category_id", 0)
    name = body_value(data, "name", "")
    price = body_value(data, "price", 0)
    stock = body_value(data, "stock", 0)
    conn = get_conn()
    cur = conn.cursor()
    sql = "UPDATE products SET category_id = :1, name = :2, price = :3, stock = :4 WHERE id = :5" if DB_CLIENT == "oracle" else "UPDATE products SET category_id = %s, name = %s, price = %s, stock = %s WHERE id = %s"
    cur.execute(sql, [category_id, name, price, stock, item_id])
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"UPDATED": True})


@app.delete("/api/products/<int:item_id>")
def delete_product(item_id):
    conn = get_conn()
    cur = conn.cursor()
    sql = "DELETE FROM products WHERE id = :1" if DB_CLIENT == "oracle" else "DELETE FROM products WHERE id = %s"
    cur.execute(sql, [item_id])
    conn.commit()
    cur.close()
    conn.close()
    return ("", 204)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=True)
