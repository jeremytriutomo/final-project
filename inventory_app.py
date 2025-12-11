from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('indago.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory
                 (item TEXT PRIMARY KEY, quantity INTEGER)''')
    conn.commit()
    conn.close()

@app.route('/stock', methods=['GET'])
def get_stock():
    conn = sqlite3.connect('indago.db')
    c = conn.cursor()
    c.execute("SELECT * FROM inventory")
    stock = {row[0]: row[1] for row in c.fetchall()}
    conn.close()
    return jsonify(stock)

@app.route('/update-stock', methods=['POST'])
def update_stock():
    data = request.json
    consumption = data.get('consumption')
    if not consumption:
        return jsonify({"error": "Missing consumption"}), 400
    
    conn = sqlite3.connect('indago.db')
    c = conn.cursor()
    for item, qty in consumption.items():
        c.execute("UPDATE inventory SET quantity = quantity - ? WHERE item = ?", (qty, item))
        # Check low stock (print for MVP, could trigger procurement)
        c.execute("SELECT quantity FROM inventory WHERE item = ?", (item,))
        remaining = c.fetchone()[0]
        if remaining < 1000:  # Arbitrary threshold
            print(f"Low stock alert: {item} = {remaining}")
    conn.commit()
    conn.close()
    return jsonify({"status": "Stock updated"})

if __name__ == '__main__':
    init_db()
    app.run(port=5002)