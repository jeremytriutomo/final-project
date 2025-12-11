from flask import Flask, request, jsonify, render_template  # ⬅️ add render_template
import sqlite3
import requests
from datetime import datetime
from collections import Counter

app = Flask(__name__)

RECIPES = {
    'espresso': {'beans': 10},
    'latte': {'beans': 20, 'milk': 200}
}


def init_db():
    conn = sqlite3.connect('indago.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS production_logs
                 (id INTEGER PRIMARY KEY, produced_items TEXT, consumption TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

# ---------- UI ROUTE ----------


@app.route('/')
def home():
    return render_template('index.html')
# ------------------------------


@app.route('/inform-order', methods=['POST'])
def inform_order():
    data = request.json
    # For MVP, just log (could save if needed)
    return jsonify({"status": "Order informed", "received": data})


@app.route('/trigger-batch', methods=['POST'])
def trigger_batch():
    # Fetch weekly orders
    try:
        response = requests.get('http://localhost:5000/orders/weekly')
        orders = response.json()
    except Exception as e:
        return jsonify({"error": "Failed to fetch orders", "detail": str(e)}), 500

    # Aggregate items
    all_items = Counter()
    for order in orders:
        # assuming each order = { "items": { "espresso": 2, "latte": 1 } }
        all_items.update(order['items'])

    if not all_items:
        return jsonify({"status": "No production needed"})

    # Calculate consumption
    consumption = Counter()
    for item, count in all_items.items():
        if item in RECIPES:
            for ing, qty in RECIPES[item].items():
                consumption[ing] += qty * count

    # Save production log
    conn = sqlite3.connect('indago.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO production_logs (produced_items, consumption, timestamp) VALUES (?, ?, ?)",
        (str(dict(all_items)), str(dict(consumption)), datetime.now())
    )
    conn.commit()
    conn.close()

    # Update Inventory
    try:
        requests.post('http://localhost:5002/update-stock',
                      json={'consumption': dict(consumption)})
    except:
        # In MVP, ignore failures
        pass

    # Notify Finance (mock)
    return jsonify({
        "status": "Batch triggered",
        "produced_items": dict(all_items),
        "consumption": dict(consumption)
    })


if __name__ == '__main__':
    init_db()
    app.run(port=5001, debug=True)
