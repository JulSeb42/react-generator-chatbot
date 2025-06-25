"""App.py
Import routes + init Flask
"""

from flask import Flask
from flask_cors import CORS
import openai
import os
from langsmith import Client
from routes.chat import chat_bp
from routes.populate_from_hf import populate_bp
from utils.connect_db import base_api_url
from utils.consts import (
    OPENAI_API_KEY,
    TOKEN_SECRET,
    CLIENT_URI,
    LANGCHAIN_PROJECT,
    LANGCHAIN_TRACING_V2,
)

app = Flask(__name__)
app.secret_key = TOKEN_SECRET

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [CLIENT_URI, "http://localhost:5173", "http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    },
)
# CORS(app)
# CORS(app, origins=[CLIENT_URI])
# CORS(app, resources={r"/*": {"origins": "*"}})
# CORS(app, resources={r"/api/*": {"origins": CLIENT_URI}})
# CORS(app, resources={r"/chat/*": {"origins": CLIENT_URI}})
# CORS(app, resources={r"/populate/*": {"origins": CLIENT_URI}})
# CORS(app, resources={r"/api/*": {"origins": [CLIENT_URI, "http://localhost:5173"]}})

openai.api_key = OPENAI_API_KEY
langsmith_client = Client()


@app.route(f"{base_api_url}/", methods=["GET"])
def index():
    """Say hello

    Returns:
            string: Returns "Hello World"
    """
    return "Hello World"


@app.route(f"{base_api_url}/health", methods=["GET"])
def health_check():
    """Check if the server is running

    Returns:
        { "status", "message" }
    """
    return {"status": "healthy", "message": "Server is running"}, 200


@app.route(f"{base_api_url}/monitoring", methods=["GET"])
def monitoring_info():
    return {
        "langsmith_project": LANGCHAIN_PROJECT,
        "tracing_enabled": LANGCHAIN_TRACING_V2,
        "langsmith_url": "https://smith.langchain.com",
    }


# Routes
app.register_blueprint(chat_bp)
app.register_blueprint(populate_bp)

# In your app.py
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
