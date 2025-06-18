from flask import Flask, request
from flask_cors import CORS
from routes.chat import chat_bp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app, resources={r"/users/*": {"origins": "*"}})
CORS(app, resources={r"chat/*": {"origins": "*"}})


@app.route("/", methods=["GET"])
def index():
    return "Hello World"


@app.after_request
def set_content_type(response):
    response.headers["Content-Type"] = "application/json"
    return response


# Routes
app.register_blueprint(chat_bp)
