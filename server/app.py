"""Flask application for React Code Generator AI.

This is the main Flask application that serves as the backend for an AI-powered
React code generation service. The application provides REST API endpoints for
generating React components from text descriptions and UI mockup images.

The service integrates multiple AI technologies:
- OpenAI GPT-4 for intelligent code generation
- OpenAI Vision API for UI mockup analysis
- Pinecone vector database for contextual code retrieval
- LangSmith for monitoring and tracing AI operations

Features:
    - AI-powered React component generation
    - UI mockup image analysis and code generation
    - Image upload and management via Cloudinary
    - Vector similarity search for code examples
    - Real-time chat interface for iterative development
    - Health monitoring and status endpoints

API Routes:
    - /api/chat/* - Chat and code generation endpoints
    - /api/populate/* - Data population and management endpoints
    - /api/health - Server health check
    - /api/ - Basic hello world endpoint

Dependencies:
    - Flask: Web framework
    - OpenAI: AI model integration
    - Pinecone: Vector database
    - MongoDB: Message and session storage
    - Cloudinary: Image hosting service
    - LangSmith: AI operation monitoring

Configuration:
    The application requires several environment variables:
    - OPENAI_API_KEY: OpenAI API authentication
    - PINECONE_API_KEY: Pinecone database access
    - MONGODB_URI: Database connection string
    - CLOUDINARY_*: Image service credentials
    - CLIENT_URI: Frontend application URL

CORS Configuration:
    Configured to allow cross-origin requests from the frontend application
    and development servers (localhost:5173, localhost:3000).

Usage:
    Run directly: python app.py
    Or with gunicorn: gunicorn app:app

Example:
    # Start the development server
    python app.py

    # The server will be available at http://localhost:8000
    # API endpoints will be available at http://localhost:8000/api/*

Note:
    This application is designed for the Ironhack AI Bootcamp Final Project
    and demonstrates integration of multiple AI services for code generation.
"""

import os
from flask import Flask
from flask_cors import CORS
import openai
from langsmith import Client
from routes.chat import chat_bp
from routes.populate_from_hf import populate_bp
from utils.connect_db import BASE_API_URL
from utils.consts import (
    OPENAI_API_KEY,
    TOKEN_SECRET,
    CLIENT_URI,
)

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
client = openai.OpenAI(api_key=OPENAI_API_KEY)
langsmith_client = Client()


@app.route(f"{BASE_API_URL}/", methods=["GET"])
def index():
    """Say hello

    Returns:
            string: Returns "Hello World"
    """
    return "Hello World"


@app.route(f"{BASE_API_URL}/health", methods=["GET"])
def health_check():
    """Check if the server is running

    Returns:
        { "status", "message" }
    """
    return {"status": "healthy", "message": "Server is running"}, 200


# Routes
app.register_blueprint(chat_bp)
app.register_blueprint(populate_bp)

# Run the app on port 8000
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
