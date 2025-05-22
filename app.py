from flask import Flask, render_template
from flask_cors import CORS
from api.endpoints import register_routes

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)
register_routes(app)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
