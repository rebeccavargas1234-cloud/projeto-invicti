from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session

# Store animals (in memory - for demonstration)
animals = []

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
        # Allow any login attempt
        session['logged_in'] = True
        return redirect(url_for('register_animal'))
    return render_template("login.html")

@app.route("/register_animal", methods=['GET', 'POST'])
def register_animal():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        animal = {
            'name': request.form.get('name'),
            'species': request.form.get('species'),
            'age': request.form.get('age')
        }
        animals.append(animal)
        return redirect(url_for('register_animal'))
    
    return render_template("register_animal.html", animals=animals)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


# ----------------------
# INTENTIONALLY VULNERABLE ENDPOINT (for local testing only)
# WARNING: do NOT deploy this to production or expose publicly.
import sqlite3
# in-memory DB for demo
_conn = sqlite3.connect(':memory:', check_same_thread=False)
_cur = _conn.cursor()
_cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
_cur.execute("INSERT INTO users (username, password) VALUES ('alice','alicepass')")
_conn.commit()

@app.route('/vuln-login', methods=['GET','POST'])
def vuln_login():
    """
    Simple SQL Injection vulnerable login endpoint.
    POST parameters: username, password
    Returns "Logged in as: <username>" if match found, otherwise "Invalid credentials".
    """
    if request.method == 'POST':
        user = request.form.get('username','')
        pwd = request.form.get('password','')
        # VULNERABLE: concatenated SQL string (SQL INJECTION)
        sql = f"SELECT id, username FROM users WHERE username = '{user}' AND password = '{pwd}' LIMIT 1"
        try:
            row = _cur.execute(sql).fetchone()
        except Exception as e:
            return 'Error', 500
        if row:
            return 'Logged in as: ' + row[1]
        return 'Invalid credentials'
    # simple form for testing
    return '''<form method="post">
                Username: <input name="username"><br>
                Password: <input name="password"><br>
                <button type="submit">Login</button>
              </form>'''
# ----------------------
