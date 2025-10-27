from flask import Flask, render_template, request, redirect, url_for, session
import subprocess, pickle, base64
from flask import render_template_string

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
# VULNERABLE ENDPOINT (SSTI - Server Side Template Injection)
# ---------------------------
@app.route("/render", methods=['GET','POST'])
def render_user_template():
    """
    Renders user-supplied template directly with Jinja2 -> SSTI vulnerability.
    GET: shows a form
    POST: renders the content of the 'tpl' field using render_template_string (DANGEROUS)
    """
    if request.method == 'GET':
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
# End of file
# ---------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

