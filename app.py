from flask import Flask, render_template, request, redirect, url_for, session
import subprocess
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

@app.route('/vuln-cmd', methods=['GET','POST'])
def vuln_cmd():
    # parameter "host" expected
    host = request.values.get('host', '')
    # VULNERABLE: concatenation into shell command -> command injection
    cmd = f"ping -c 1 {host}"
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5)
        return out.decode(errors='ignore')
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output.decode(errors='ignore')}", 500
    except Exception as e:
        return f"Exec error: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

