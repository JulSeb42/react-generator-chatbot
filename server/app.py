"""App.py
Import routes + init Flask
"""

from flask import Flask
from flask_cors import CORS
from routes.chat import chat_bp
from utils.connect_db import base_api_url

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app, resources={r"/users/*": {"origins": "*"}})
CORS(app, resources={r"chat/*": {"origins": "*"}})


@app.route(f"{base_api_url}/", methods=["GET"])
def index():
    """Say hello

    Returns:
            string: Returns "Hello World"
    """
    return "Hello World"


@app.after_request
def set_content_type(response):
    """Sets headers for CORS

    Args:
            response (_type_): _description_

    Returns:
            _type_: _description_
    """
    response.headers["Content-Type"] = "application/json"
    return response


# Routes
app.register_blueprint(chat_bp)
