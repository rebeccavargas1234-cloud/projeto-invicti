from flask import Flask, render_template, request, redirect, url_for, session
import subprocess, pickle, base64

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

# ---------------------------
# VULNERABLE ENDPOINT (Command Injection)
# ---------------------------
# WARNING: intentionally vulnerable. Use only in a local/test environment.
@app.route("/ping", methods=['GET','POST'])
def ping_host():
    """
    Expects parameter 'host' (from query string or form).
    This endpoint builds a shell command concatenating user input and executes it.
    This is VULNERABLE to command injection (e.g., host = "8.8.8.8; id").
    """
    host = request.values.get('host', '').strip()
    if not host:
        return '''
            <form method="post">
                Host to ping: <input name="host"><br>
                <button type="submit">Ping</button>
            </form>
        '''
    # VULNERABLE: using shell=True with concatenated string
    cmd = f"ping -c 1 {host}"
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5)
        return "<pre>" + output.decode(errors='ignore') + "</pre>"
    except subprocess.CalledProcessError as e:
        return "<pre>Command failed:\n" + e.output.decode(errors='ignore') + "</pre>", 500
    except Exception as e:
        return f"Execution error: {e}", 500


# ----------------------
# INTENTIONALLY VULNERABLE ENDPOINT: Insecure Deserialization (Pickle) - LAB ONLY
# ----------------------

@app.route('/vuln-pickle', methods=['POST'])
def vuln_pickle():
    """
    Expects raw base64-encoded pickle in the request body. Demonstrates insecure deserialization -> RCE risk.
    Use only in isolated test environment.
    """
    b64 = request.get_data(as_text=True) or ''
    if not b64:
        return ("Send base64-encoded pickled payload in request body.\n", 400)
    try:
        data = base64.b64decode(b64)
        # VULNERABLE: untrusted pickle deserialization -> may lead to remote code execution
        obj = pickle.loads(data)
    except Exception as e:
        return (f"Deserialization error: {e}\n", 400)
    return (f"Loaded object: {repr(obj)}\n", 200)
# ----------------------


# ---------------------------
# End of file
# ---------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

