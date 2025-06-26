from flask import Blueprint, jsonify, request
import uuid
import datetime
import openai
from langsmith import traceable
import base64
from utils.connect_db import base_api_url, messages_col, snippets_col
from utils.pc_index import index
from utils.langchain_service import react_assistant
from utils.cloudinary_service import cloudinary_service

chat_bp = Blueprint("chat", __name__)
base_api_url = f"{base_api_url}/chat"


@chat_bp.route(f"{base_api_url}/new-chat", methods=["POST"])
@traceable(run_type="tool", name="chat_endpoint")
def chat():
    try:
        # Step 1: Parse request data
        try:
            data = request.get_json()
        except Exception as json_error:
            return jsonify({"error": f"Invalid JSON: {str(json_error)}"}), 400

        user_input = data.get("message", "") if data else ""
        session_id = data.get("session_id") if data else None
        image_url = data.get("image_url") if data else None

        # Step 3: Generate session ID if needed
        if not session_id:
            session_id = str(uuid.uuid4())

        if not user_input and not image_url:
            return jsonify({"error": "No message or image provided"}), 400

        # Step 5: Image analysis (if image provided)
        image_description = ""
        if image_url:
            try:
                import requests

                response = requests.get(image_url, timeout=10)  # Reduced timeout
                response.raise_for_status()
                image_data = response.content

                base64_image = base64.b64encode(image_data).decode("utf-8")

                try:
                    image_description = react_assistant.analyze_image(base64_image)
                except Exception as vision_error:
                    image_description = "Image analysis failed"

            except Exception as image_error:
                image_description = "Image processing failed"
                print("Error: " + image_error)

        # Step 6: Prepare AI input
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

        # Step 7: Save user message
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
        try:
            reply = react_assistant.generate_code(
                user_input=ai_input,
                image_description=(
                    image_description
                    if image_description and "failed" not in image_description.lower()
                    else None
                ),
            )
        except Exception as ai_error:
            # Simple fallback response
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

        # Step 9: Save assistant response
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

        # Step 10: Prepare response
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
        import traceback

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


@chat_bp.route(f"{base_api_url}/messages/<session_id>", methods=["GET"])
def get_session_messages(session_id):
    res = messages_col.find({"session_id": str(session_id)})
    messages = list(res)
    for message in messages:
        message["_id"] = str(message["_id"])
    return jsonify(messages), 201


@chat_bp.route(f"{base_api_url}/delete-session/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    messages_col.delete_many({"session_id": session_id})
    return "Your session has been deleted!"


@chat_bp.route(f"{base_api_url}/add-snippet", methods=["POST"])
def add_snippet():
    data = request.get_json()
    text = data["text"]
    tags = data.get("tags", [])

    # Store in DB
    result = snippets_col.insert_one(
        {
            "text": text,
            "tags": tags,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
    )

    # Generate and upload to Pinecone
    embedding = openai.Embedding.create(input=text, model="text-embedding-ada-002")[
        "data"
    ][0]["embedding"]
    index.upsert(
        [(str(result.inserted_id), embedding, {"text": text, "tags": ",".join(tags)})]
    )
    return jsonify({"status": "added"})


@chat_bp.route(f"{base_api_url}/upload-image", methods=["POST"])
def upload_image():
    """Upload image to Cloudinary immediately"""
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
        else:
            return (
                jsonify({"error": f"Upload failed: {cloudinary_result.get('error')}"}),
                500,
            )

    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({"error": str(e)}), 500
