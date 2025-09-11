from flask import Flask, render_template

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
