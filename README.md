# Logistics Dashboard

A portfolio-ready logistics operations dashboard built with **Python, Flask, SQLite and REST APIs**.

## Features

- Create and track deliveries
- Assign drivers to shipments
- Update delivery status from the dashboard
- Filter shipments by operational status
- KPI cards for planned, in-transit, delivered and delayed shipments
- Persistent SQLite storage
- REST API endpoints
- Responsive dashboard UI
- Health-check endpoint

## Tech Stack

- Python 3
- Flask
- SQLite
- HTML / CSS / JavaScript

## API

- `GET /api/deliveries` — list deliveries
- `POST /api/deliveries` — create a delivery
- `PATCH /api/deliveries/<id>` — update delivery status
- `GET /health` — service health check

Example request:

```json
{
  "customer": "Example Store",
  "destination": "Bucharest",
  "driver": "Alex",
  "status": "planned"
}
```

## Run Locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5001`.

## Portfolio Note

This project demonstrates CRUD-style backend development, REST API design, SQLite persistence and a responsive operations dashboard.
