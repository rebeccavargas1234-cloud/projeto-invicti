from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/border")
def border():
    return render_template("border.html")

@app.route("/labrador")
def labrador():
    return render_template("labrador.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Basic validation - this is just for demonstration
        if username == "admin" and password == "admin":
            return redirect(url_for('home'))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

# API Routes
@app.route("/api/items", methods=['GET'])
def get_items():
    return jsonify(items)

@app.route("/api/items", methods=['POST'])
def create_item():
    data = request.get_json()
    if 'name' not in data:
        return jsonify({"error": "Name is required"}), 400
    item = {
        "id": len(items) + 1,
        "name": data['name'],
        "description": data.get('description', '')
    }
    items.append(item)
    return jsonify(item), 201

@app.route("/api/items/<int:item_id>", methods=['GET'])
def get_item(item_id):
    item = next((item for item in items if item['id'] == item_id), None)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item)

@app.route("/api/items/<int:item_id>", methods=['PUT'])
def update_item(item_id):
    item = next((item for item in items if item['id'] == item_id), None)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    data = request.get_json()
    item['name'] = data.get('name', item['name'])
    item['description'] = data.get('description', item['description'])
    return jsonify(item)

@app.route("/api/items/<int:item_id>", methods=['DELETE'])
def delete_item(item_id):
    global items
    items = [item for item in items if item['id'] != item_id]
    return '', 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
