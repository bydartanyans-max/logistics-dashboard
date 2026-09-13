from pathlib import Path
import sqlite3
from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "logistics.db"

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

        counts = {
            "total": conn.execute("SELECT COUNT(*) FROM deliveries").fetchone()[0],
            "planned": conn.execute("SELECT COUNT(*) FROM deliveries WHERE status='planned'").fetchone()[0],
            "in_transit": conn.execute("SELECT COUNT(*) FROM deliveries WHERE status='in_transit'").fetchone()[0],
            "delivered": conn.execute("SELECT COUNT(*) FROM deliveries WHERE status='delivered'").fetchone()[0],
            "delayed": conn.execute("SELECT COUNT(*) FROM deliveries WHERE status='delayed'").fetchone()[0],
        }

    return render_template("dashboard.html", deliveries=rows, counts=counts, active_status=status)


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "logistics-dashboard"})


@app.route("/api/deliveries", methods=["GET", "POST"])
def deliveries_api():
    if request.method == "GET":
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM deliveries ORDER BY id DESC").fetchall()
        return jsonify([dict(row) for row in rows])

    data = request.get_json(silent=True) or {}
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
        row = conn.execute(
            "SELECT * FROM deliveries WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()

    return jsonify(dict(row)), 201


@app.patch("/api/deliveries/<int:delivery_id>")
def update_delivery(delivery_id):
    data = request.get_json(silent=True) or {}
    status = str(data.get("status", "")).strip()
    if status not in VALID_STATUSES:
        return jsonify({"error": "invalid status"}), 400

    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM deliveries WHERE id = ?", (delivery_id,)
        ).fetchone()
        if not existing:
            return jsonify({"error": "delivery not found"}), 404

        conn.execute(
            "UPDATE deliveries SET status = ? WHERE id = ?", (status, delivery_id)
        )
        row = conn.execute(
            "SELECT * FROM deliveries WHERE id = ?", (delivery_id,)
        ).fetchone()

    return jsonify(dict(row))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5001)
