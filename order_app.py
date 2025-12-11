from flask import Flask, request, jsonify
import sqlite3
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('indago.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY, items TEXT, total INTEGER, timestamp DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS inventory
                 (item TEXT PRIMARY KEY, quantity INTEGER)''')
    # Seed initial inventory if empty
    c.execute("INSERT OR IGNORE INTO inventory (item, quantity) VALUES ('beans', 10000)")
    c.execute("INSERT OR IGNORE INTO inventory (item, quantity) VALUES ('milk', 100000)")
    conn.commit()
    conn.close()

@app.route('/orders', methods=['POST'])
def place_order():
    data = request.json
    items = data.get('items')
    total = data.get('total')
    if not items or not total:
        return jsonify({"error": "Missing data"}), 400
    
    conn = sqlite3.connect('indago.db')
    c = conn.cursor()
    c.execute("INSERT INTO orders (items, total, timestamp) VALUES (?, ?, ?)",
              (str(items), total, datetime.now()))
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    
    # Inform Kitchen
    try:
        requests.post('http://localhost:5001/inform-order', json={'order_id': order_id, 'items': items})
    except:
        pass  # Ignore for MVP
    
    # Inform Finance
    try:
        requests.post('http://localhost:5003/create-invoice', json={'order_id': order_id, 'amount': total})
    except:
        pass
    
    return jsonify({"status": "Order placed", "id": order_id}), 201

@app.route('/orders/weekly', methods=['GET'])
def get_weekly_orders():
    conn = sqlite3.connect('indago.db')
    c = conn.cursor()
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
    c.execute("SELECT items FROM orders WHERE timestamp > ?", (seven_days_ago,))
    orders = [{'items': eval(row[0])} for row in c.fetchall()]  # eval for JSON-like
    conn.close()
    return jsonify(orders)

if __name__ == '__main__':
    init_db()
    app.run(port=5000)