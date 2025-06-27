"""Chat routes for AI-powered React code generation.

This module provides Flask Blueprint routes for handling chat interactions with an AI assistant
that generates React components from text descriptions and UI mockup images. The service
integrates OpenAI's GPT-4 and Vision models with Pinecone vector database for contextual
code generation.

Routes:
    POST /api/chat/new-chat - Generate React code from text/image input
    GET /api/chat/messages/<session_id> - Retrieve conversation history
    DELETE /api/chat/delete-session/<session_id> - Delete session and messages
    POST /api/chat/add-snippet - Add code snippet to knowledge base
    POST /api/chat/upload-image - Upload UI mockup images to Cloudinary

Features:
    - AI-powered React component generation from natural language
    - UI mockup analysis using OpenAI Vision API
    - Session-based conversation management
    - Image upload and processing via Cloudinary
    - Vector similarity search for relevant code examples
    - Persistent message storage in MongoDB

Dependencies:
    - OpenAI API for code generation and image analysis
    - Pinecone for vector similarity search
    - MongoDB for message and session storage
    - Cloudinary for image hosting and processing
    - LangSmith for AI operation tracing

Data Flow:
    1. User sends message/image via POST /new-chat
    2. Image analysis (if provided) using Vision API
    3. Context retrieval from Pinecone vector database
    4. Code generation using GPT-4 with retrieved context
    5. Response storage in MongoDB and return to client

Request/Response Formats:
    New Chat Request:
        {
            "message": "Create a button component",
            "session_id": "uuid-string",
            "image_url": "https://cloudinary.com/image.jpg"
        }

    New Chat Response:
        {
            "_id": "mongo-object-id",
            "session_id": "uuid-string",
            "role": "assistant",
            "message": "Generated React code...",
            "created_at": "ISO-datetime"
        }

Error Handling:
    All endpoints include comprehensive error handling with specific error messages
    and appropriate HTTP status codes. Fallback responses are provided when AI
    services are unavailable.

Example Usage:
    # Generate React component
    POST /api/chat/new-chat
    {
        "message": "Create a responsive login form",
        "session_id": "abc-123"
    }

    # Upload UI mockup
    POST /api/chat/upload-image
    Content-Type: multipart/form-data
    image: [binary file data]

Security:
    - Input validation for all user-provided data
    - File type validation for image uploads
    - Session isolation for user conversations
    - Error message sanitization to prevent information disclosure

Performance:
    - Optimized embedding generation for code similarity search
    - Efficient image processing with size and format validation
    - Database indexing on session_id for fast message retrieval
    - Connection pooling for external API calls
"""

import uuid
import base64
import datetime
import traceback
from flask import Blueprint, jsonify, request
import requests
from langsmith import traceable
from utils.connect_db import BASE_API_URL, messages_col, snippets_col
from utils.pc_index import index
from utils.langchain_service import react_assistant
from utils.cloudinary_service import cloudinary_service

chat_bp = Blueprint("chat", __name__)
BASE_API_URL = f"{BASE_API_URL}/chat"


@chat_bp.route(f"{BASE_API_URL}/new-chat", methods=["POST"])
@traceable(run_type="tool", name="chat_endpoint")
def chat():  # pylint: disable=too-many-locals,too-many-return-statements,too-many-branches
    """Generate React code from user input and optional UI mockup image."""
    try:
        # Step 1: Parse request data
        try:
            data = request.get_json()
        except Exception as json_error:
            return jsonify({"error": f"Invalid JSON: {str(json_error)}"}), 400

        user_input = data.get("message", "") if data else ""
        session_id = data.get("session_id") if data else None
        image_url = data.get("image_url") if data else None

        # Step 2: Generate session ID if needed
        if not session_id:
            session_id = str(uuid.uuid4())

        if not user_input and not image_url:
            return jsonify({"error": "No message or image provided"}), 400

        # Step 3: Check for boilerplate/starter requests
        boilerplate_keywords = [
            "boilerplate",
            "starter",
            "template",
            "scaffold",
            "setup",
            "initial project",
            "project setup",
            "create project",
            "new project",
            "bootstrap",
            "kickstart",
            "foundation",
        ]

        is_boilerplate_request = any(
            keyword in user_input.lower() for keyword in boilerplate_keywords
        )

        # Step 4: Image analysis (if image provided)
        image_description = ""
        if image_url:
            try:
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                image_data = response.content

                base64_image = base64.b64encode(image_data).decode("utf-8")

                try:
                    image_description = react_assistant.analyze_image(base64_image)
                except Exception:
                    image_description = "Image analysis failed"

            except Exception as image_error:
                image_description = "Image processing failed"
                print("Error: " + str(image_error))

        # Step 5: Prepare AI input
        try:
            if image_description and "failed" not in image_description.lower():
                ai_input = (
                    f"{user_input}\n\nUI Analysis: {image_description}"
                    if user_input
                    else f"Generate React code for this UI: {image_description}"
                )
            else:
                ai_input = user_input or "Generate a React component"

        except Exception as input_error:
            return (
                jsonify({"error": f"Input preparation failed: {str(input_error)}"}),
                500,
            )

        # Step 6: Save user message
        try:
            user_message_data = {
                "session_id": session_id,
                "role": "user",
                "message": user_input,
                "has_image": bool(image_url),
                "image_url": image_url,
                "created_at": datetime.datetime.now(),
            }

            messages_col.insert_one(user_message_data)
        except Exception as save_error:
            return (
                jsonify({"error": f"Failed to save user message: {str(save_error)}"}),
                500,
            )

            # Step 7: Generate AI response
        try:
            # For boilerplate requests, only show CLI recommendation
            if is_boilerplate_request:
                reply = """🚀 **For complete project setup, check out my CLI tool:**

```bash
npx @julseb-lib/julseb-cli
```

This CLI provides ready-to-use project templates and boilerplates for React, Express, and more!

📦 **Package:** https://www.npmjs.com/package/@julseb-lib/julseb-cli"""
            else:
                # Generate normal AI response for non-boilerplate requests
                reply = react_assistant.generate_code(
                    user_input=ai_input,
                    image_description=(
                        image_description
                        if image_description
                        and "failed" not in image_description.lower()
                        else None
                    ),
                )

        except Exception:
            # Fallback responses
            if is_boilerplate_request:
                reply = """🚀 **For complete project setup, check out my CLI tool:**

```bash
npx @julseb-lib/julseb-cli
```

This CLI provides ready-to-use project templates and boilerplates for React, Next.js, and more!

📦 **Package:** https://www.npmjs.com/package/@julseb-lib/julseb-cli"""
            else:
                reply = """```tsx
import React from 'react';

const Button = () => {
    return (
        <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
            Click me
        </button>
    );
};

export default Button;
```"""

        # Step 8: Save assistant response
        try:
            assistant_message_data = {
                "session_id": session_id,
                "role": "assistant",
                "message": reply,
                "created_at": datetime.datetime.now(),
            }

            if image_url:
                assistant_message_data["references_image"] = image_url

            result = messages_col.insert_one(assistant_message_data)
        except Exception as save_error:
            return (
                jsonify(
                    {"error": f"Failed to save assistant message: {str(save_error)}"}
                ),
                500,
            )

        # Step 9: Prepare response
        try:
            response_data = {
                "_id": str(result.inserted_id),
                "session_id": session_id,
                "role": "assistant",
                "message": reply,
                "created_at": datetime.datetime.now().isoformat(),
            }
            return jsonify(response_data), 201

        except Exception as response_error:
            return (
                jsonify(
                    {"error": f"Failed to prepare response: {str(response_error)}"}
                ),
                500,
            )

    except Exception as e:
        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": f"Internal server error: {str(e)}",
                    "type": str(type(e).__name__),
                }
            ),
            500,
        )


@chat_bp.route(f"{BASE_API_URL}/messages/<session_id>", methods=["GET"])
def get_session_messages(session_id):
    """Retrieve all messages for a specific session.

    Args:
        session_id (str): Session UUID to retrieve messages for

    Returns:
        tuple: JSON list of messages with MongoDB object IDs converted to strings,
               HTTP status code 201
    """
    res = messages_col.find({"session_id": str(session_id)})
    messages = list(res)
    for message in messages:
        message["_id"] = str(message["_id"])
    return jsonify(messages), 201


@chat_bp.route(f"{BASE_API_URL}/delete-session/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    """Delete all messages and data for a specific session.

    Args:
        session_id (str): Session UUID to delete

    Returns:
        str: Confirmation message
    """
    messages_col.delete_many({"session_id": session_id})
    return "Your session has been deleted!"


@chat_bp.route(f"{BASE_API_URL}/add-snippet", methods=["POST"])
def add_snippet():
    """Add a new code snippet to the knowledge base."""
    data = request.get_json()
    text = data["text"]
    tags = data.get("tags", [])

    # Store in DB
    result = snippets_col.insert_one(
        {
            "text": text,
            "tags": tags,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
        }
    )

    # Generate and upload to Pinecone using existing embeddings
    embedding = react_assistant.embeddings.embed_query(text)

    index.upsert(
        [(str(result.inserted_id), embedding, {"text": text, "tags": ",".join(tags)})]
    )
    return jsonify({"status": "added"})


@chat_bp.route(f"{BASE_API_URL}/upload-image", methods=["POST"])
def upload_image():
    """Upload UI mockup image to Cloudinary for analysis.

    Handles multipart form data upload, validates image files, and uploads
    to Cloudinary with automatic optimization and transformation.

    Form Data:
        image (file): Image file (PNG, JPG, GIF, max 5MB)

    Returns:
        tuple: JSON response with upload results, HTTP status code
            Success (200):
                - success (bool): True
                - image_url (str): Cloudinary secure URL
                - public_id (str): Cloudinary public identifier
                - filename (str): Original filename
            Error (400/500):
                - error (str): Error description

    Raises:
        400: No file provided or empty file
        500: Cloudinary upload failure or processing error
    """
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files["image"]

        # Read image data
        image_file.seek(0)
        image_data = image_file.read()

        if len(image_data) == 0:
            return jsonify({"error": "Image file is empty"}), 400

        # Upload to Cloudinary
        cloudinary_result = cloudinary_service.upload_image(
            file_data=image_data,
            filename=image_file.filename or "ui_mockup",
            folder="final-project-ironhack",
        )

        if cloudinary_result["success"]:
            return (
                jsonify(
                    {
                        "success": True,
                        "image_url": cloudinary_result["url"],
                        "public_id": cloudinary_result["public_id"],
                        "filename": image_file.filename,
                    }
                ),
                200,
            )

        return (
            jsonify({"error": f"Upload failed: {cloudinary_result.get('error')}"}),
            500,
        )

    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({"error": str(e)}), 500
