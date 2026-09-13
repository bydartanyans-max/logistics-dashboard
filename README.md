# Logistics Operations Dashboard 🚚

A portfolio-ready logistics operations application built with **Python, Flask, SQLite, REST APIs, automated tests, CI and Docker**.

The project models a small real-world delivery workflow: shipments can be created, assigned to drivers, filtered, searched and moved through operational statuses while KPI endpoints provide a quick overview of fleet activity.

## ✨ Features

- Create and track deliveries
- Assign or reassign drivers
- Update delivery status
- Filter by status or driver
- Search by customer, destination or driver
- KPI summary endpoint for operational metrics
- Persistent SQLite storage
- REST API with validation and error handling
- Responsive dashboard UI
- Health-check endpoint
- Pytest test suite
- GitHub Actions CI
- Docker support
- Environment-based database and port configuration

## 📊 Delivery workflow

```text
planned → in_transit → delivered
              └────→ delayed
```

Supported statuses:

- `planned`
- `in_transit`
- `delivered`
- `delayed`

## 🧰 Tech Stack

`Python` · `Flask` · `SQLite` · `REST API` · `HTML` · `CSS` · `Pytest` · `GitHub Actions` · `Docker`

## 🔌 API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/deliveries` | List deliveries |
| `POST` | `/api/deliveries` | Create a delivery |
| `GET` | `/api/deliveries/<id>` | Retrieve one delivery |
| `PATCH` | `/api/deliveries/<id>` | Update status and/or driver |
| `GET` | `/api/summary` | Get KPI counts |
| `GET` | `/health` | Service health check |

### Filters

Examples:

```text
/api/deliveries?status=delivered
/api/deliveries?driver=Alex
/api/deliveries?q=Bucharest
```

### Create delivery

```json
{
  "customer": "Example Store",
  "destination": "Bucharest",
  "driver": "Alex",
  "status": "planned"
}
```

### Update delivery

```json
{
  "status": "in_transit",
  "driver": "Maria"
}
```

## ▶️ Run locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:5001
```

Optional environment variables:

```bash
LOGISTICS_DB=/path/to/logistics.db
PORT=5001
FLASK_DEBUG=0
```

## 🐳 Docker

```bash
docker build -t logistics-dashboard .
docker run -p 5001:5001 logistics-dashboard
```

## 🧪 Tests

```bash
pip install pytest
python -m pytest -q
```

GitHub Actions runs the test suite automatically on pushes and pull requests to `main`.

## 💼 Portfolio Focus

This repository demonstrates practical backend development for an operations use case: REST API design, validation, persistence, filtering, KPI reporting, automated testing, CI and containerization.

It is designed as a compact example of how a real logistics or delivery workflow can be translated into a maintainable backend service.
