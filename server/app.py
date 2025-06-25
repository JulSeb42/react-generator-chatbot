"""App.py
Import routes + init Flask
"""

from flask import Flask
from flask_cors import CORS
import openai
import os
from routes.chat import chat_bp
from routes.populate_from_hf import populate_bp
from utils.connect_db import base_api_url
from utils.consts import OPENAI_API_KEY, TOKEN_SECRET, CLIENT_URI

app = Flask(__name__)
app.secret_key = TOKEN_SECRET
CORS(app)
CORS(app, origins=[CLIENT_URI])
CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app, resources={r"/api/*": {"origins": CLIENT_URI}})
CORS(app, resources={r"/chat/*": {"origins": CLIENT_URI}})
CORS(app, resources={r"/populate/*": {"origins": CLIENT_URI}})
CORS(app, resources={r"/api/*": {"origins": [CLIENT_URI, "http://localhost:5173"]}})

openai.api_key = OPENAI_API_KEY


@app.route(f"{base_api_url}/", methods=["GET"])
def index():
    """Say hello

    Returns:
            string: Returns "Hello World"
    """
    return "Hello World"


# @app.after_request
# def set_content_type(response):
#     """Sets headers for CORS

#     Args:
#             response (_type_): _description_

#     Returns:
#             _type_: _description_
#     """
#     response.headers["Content-Type"] = "application/json"
#     return response


# Routes
app.register_blueprint(chat_bp)
app.register_blueprint(populate_bp)

# In your app.py
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
