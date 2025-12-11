Indago Production Orchestrator

A Flask-based microservice that aggregates weekly coffee orders, calculates ingredient consumption, updates inventory, stores production logs, and provides a simple UI.

🚀 Features

Receives order notifications (/inform-order)

Triggers weekly production batches (/trigger-batch)

Calculates ingredient consumption based on recipes

Saves production logs into SQLite

Integrates with:

Order Service (localhost:5000)

Inventory Service (localhost:5002)

Simple homepage UI (/)

🧱 Tech Stack

Python + Flask

SQLite (local database)

Requests for service-to-service communication

Runs on port 5001

📦 Installation
pip install flask requests


Run the service:

python app.py


On startup, the app automatically creates indago.db and initializes the table.

🗂 Database Schema
Table: production_logs
Column	Type	Description
id	INTEGER	Primary key
produced_items	TEXT	Stringified dict of drink quantities
consumption	TEXT	Stringified dict of ingredient usage
timestamp	DATETIME	When the batch was recorded

Example stored values:

produced_items = {"espresso": 3, "latte": 1}
consumption = {"beans": 50, "milk": 200}

🍵 Recipes

Used for ingredient calculation during production:

RECIPES = {
    'espresso': {'beans': 10},
    'latte': {'beans': 20, 'milk': 200}
}

📘 API Documentation

Base URL:

http://localhost:5001

1️⃣ GET /

Renders index.html.

Request

GET /


Response

200 OK

HTML content

2️⃣ POST /inform-order

Receives order information.
In MVP, the payload is not stored, only returned as confirmation.

Request
POST /inform-order
Content-Type: application/json


Example body:

{
  "order_id": "ORD-123",
  "items": { "espresso": 2, "latte": 1 },
  "total_amount": 75000,
  "status": "PAID"
}

Response
{
  "status": "Order informed",
  "received": { ... original payload ... }
}

cURL Example
curl -X POST http://localhost:5001/inform-order \
  -H "Content-Type: application/json" \
  -d '{"order_id":"ORD-123","items":{"espresso":2,"latte":1}}'

3️⃣ POST /trigger-batch

Aggregates weekly orders → computes consumption → logs production → updates inventory.

🔗 External Dependencies
GET http://localhost:5000/orders/weekly

Expected response:

[
  { "items": { "espresso": 2, "latte": 1 } },
  { "items": { "espresso": 1 } }
]

POST http://localhost:5002/update-stock

Sent body:

{
  "consumption": {
    "beans": 50,
    "milk": 200
  }
}


Inventory failure is ignored in MVP.

Request
POST /trigger-batch


No body required.

Successful Response (if orders exist)
{
  "status": "Batch triggered",
  "produced_items": {
    "espresso": 3,
    "latte": 1
  },
  "consumption": {
    "beans": 50,
    "milk": 200
  }
}

Response (no orders)
{
  "status": "No production needed"
}

Failure (Order Service unreachable)
{
  "error": "Failed to fetch orders",
  "detail": "<error message>"
}

cURL Example
curl -X POST http://localhost:5001/trigger-batch

🗃 Directory Structure
/
├── app.py
├── indago.db          # auto-created
└── templates/
    └── index.html

▶️ Running the Service

Install dependencies

pip install flask requests


Start the service

python app.py


Access endpoints:

UI → http://localhost:5001/

API → /inform-order, /trigger-batch