from flask import Flask, render_template, render_template_string, request, redirect, url_for, session
import subprocess, pickle, base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session

# Store animals (in memory - for demonstration)
animals = []

@app.route("/")
def home():
    # add a quick link so scanners find SSTI page
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
# VULNERABLE SSTI ENDPOINT (Server-Side Template Injection)
# ---------------------------
# WARNING: intentionally vulnerable. Use only in a local/test environment.
@app.route("/render", methods=['GET','POST'])
def render_user_template():
    """
    Renders user-supplied template directly with Jinja2 -> SSTI vulnerability.
    GET: shows a form (templates/ssti.html)
    POST: renders the content of the 'tpl' field using render_template_string (DANGEROUS)
    """
    if request.method == 'GET':
        # prefer the dedicated template if exists (more discoverable)
        try:
            return render_template("ssti.html")
        except Exception:
            # fallback HTML form if template missing
            return '''
                <h2>SSTI Test (lab only)</h2>
                <form method="post">
                  Template to render:<br>
                  <textarea name="tpl" rows="8" cols="80">{{ 7*7 }}</textarea><br>
                  <button type="submit">Render</button>
                </form>
                <p style="color:darkred;">WARNING: This endpoint intentionally vulnerable to SSTI. Use only in isolated test environment.</p>
            '''
    tpl = request.form.get('tpl','').strip()
    if not tpl:
        return "Provide template in 'tpl' form field.\n", 400
    try:
        # VULNERABLE: rendering untrusted template string -> SSTI (possible RCE)
        rendered = render_template_string(tpl)
    except Exception as e:
        return f"Template render error: {e}\n", 500
    return rendered, 200
# ---------------------------


# ---------------------------
# (Optional) Existing vulnerable endpoints kept: ping and vuln-pickle (if you want)
# ---------------------------

# Command injection example (already present in your app)
@app.route("/ping", methods=['GET','POST'])
def ping_host():
    host = request.values.get('host', '').strip()
    if not host:
        return '''
            <form method="post">
                Host to ping: <input name="host"><br>
                <button type="submit">Ping</button>
            </form>
        '''
    cmd = f"ping -c 1 {host}"
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5)
        return "<pre>" + output.decode(errors='ignore') + "</pre>"
    except subprocess.CalledProcessError as e:
        return "<pre>Command failed:\n" + e.output.decode(errors='ignore') + "</pre>", 500
    except Exception as e:
        return f"Execution error: {e}", 500

# Insecure deserialization endpoint (if you want; otherwise remove)
@app.route("/vuln-pickle", methods=['GET','POST'])
def vuln_pickle():
    if request.method == 'GET':
        return '''
            <h2>Insecure Deserialization (lab only)</h2>
            <form method="post">
              Base64 pickled payload:<br>
              <textarea name="payload_b64" rows="8" cols="80"></textarea><br>
              <button type="submit">Send payload</button>
            </form>
            <p style="color:darkred;">WARNING: This endpoint is intentionally vulnerable. Use only in isolated test environment.</p>
        '''
    b64 = request.form.get('payload_b64') or request.get_data(as_text=True) or ''
    b64 = b64.strip()
    if not b64:
        return ("Send base64-encoded pickled payload in form field 'payload_b64' or raw POST body.\n", 400)
    try:
        data = base64.b64decode(b64)
    except Exception as e:
        return (f"Base64 decode error: {e}\n", 400)
    try:
        # VULNERABLE: deserializing untrusted data with pickle.loads -> RCE risk
        obj = pickle.loads(data)
    except Exception as e:
        return (f"Deserialization error / exception: {e}\n", 500)
    return (f"Loaded object: {repr(obj)}\n", 200)


# ---------------------------
# End of file
# ---------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
