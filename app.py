import os
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("LOGISTICS_DB", BASE_DIR / "logistics.db"))

app = Flask(__name__)

VALID_STATUSES = {"planned", "in_transit", "delivered", "delayed"}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS deliveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer TEXT NOT NULL,
                destination TEXT NOT NULL,
                driver TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'planned',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def delivery_to_dict(row):
    return dict(row)


def status_counts(conn):
    counts = {"total": conn.execute("SELECT COUNT(*) FROM deliveries").fetchone()[0]}
    for status in VALID_STATUSES:
        counts[status] = conn.execute(
            "SELECT COUNT(*) FROM deliveries WHERE status = ?", (status,)
        ).fetchone()[0]
    return counts


@app.get("/")
def dashboard():
    status = request.args.get("status", "all")
    with get_db() as conn:
        if status in VALID_STATUSES:
            rows = conn.execute(
                "SELECT * FROM deliveries WHERE status = ? ORDER BY id DESC", (status,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM deliveries ORDER BY id DESC").fetchall()
        counts = status_counts(conn)

    return render_template(
        "dashboard.html", deliveries=rows, counts=counts, active_status=status
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "logistics-dashboard"})


@app.get("/api/summary")
def summary():
    with get_db() as conn:
        return jsonify(status_counts(conn))


@app.route("/api/deliveries", methods=["GET", "POST"])
def deliveries_api():
    if request.method == "GET":
        status = request.args.get("status", "").strip()
        driver = request.args.get("driver", "").strip()
        search = request.args.get("q", "").strip()

        sql = "SELECT * FROM deliveries"
        where = []
        params = []

        if status:
            if status not in VALID_STATUSES:
                return jsonify({"error": "invalid status"}), 400
            where.append("status = ?")
            params.append(status)
        if driver:
            where.append("driver LIKE ?")
            params.append(f"%{driver}%")
        if search:
            where.append("(customer LIKE ? OR destination LIKE ? OR driver LIKE ?)")
            term = f"%{search}%"
            params.extend([term, term, term])
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY id DESC"

        with get_db() as conn:
            rows = conn.execute(sql, params).fetchall()
        return jsonify([delivery_to_dict(row) for row in rows])

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON body is required"}), 400

    customer = str(data.get("customer", "")).strip()
    destination = str(data.get("destination", "")).strip()
    driver = str(data.get("driver", "")).strip()
    status = str(data.get("status", "planned")).strip()

    if not customer or not destination:
        return jsonify({"error": "customer and destination are required"}), 400
    if status not in VALID_STATUSES:
        return jsonify({"error": "invalid status"}), 400

    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO deliveries(customer, destination, driver, status) VALUES (?, ?, ?, ?)",
            (customer, destination, driver, status),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM deliveries WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()

    return jsonify(delivery_to_dict(row)), 201


@app.get("/api/deliveries/<int:delivery_id>")
def get_delivery(delivery_id):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM deliveries WHERE id = ?", (delivery_id,)
        ).fetchone()
    if row is None:
        return jsonify({"error": "delivery not found"}), 404
    return jsonify(delivery_to_dict(row))


@app.patch("/api/deliveries/<int:delivery_id>")
def update_delivery(delivery_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON body is required"}), 400

    allowed_fields = {"status", "driver"}
    if not any(field in data for field in allowed_fields):
        return jsonify({"error": "status or driver is required"}), 400

    with get_db() as conn:
        existing = conn.execute(
            "SELECT * FROM deliveries WHERE id = ?", (delivery_id,)
        ).fetchone()
        if not existing:
            return jsonify({"error": "delivery not found"}), 404

        status = str(data.get("status", existing["status"])).strip()
        driver = str(data.get("driver", existing["driver"])).strip()

        if status not in VALID_STATUSES:
            return jsonify({"error": "invalid status"}), 400

        conn.execute(
            "UPDATE deliveries SET status = ?, driver = ? WHERE id = ?",
            (status, driver, delivery_id),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM deliveries WHERE id = ?", (delivery_id,)
        ).fetchone()

    return jsonify(delivery_to_dict(row))


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5001")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
