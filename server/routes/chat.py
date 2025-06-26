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


@chat_bp.route(f"{base_api_url}/test", methods=["GET", "POST"])
def test_chat_route():
    return {
        "message": "LangChain-powered chat is working!",
        "method": request.method,
    }, 200


@chat_bp.route(f"{base_api_url}/new-chat", methods=["POST"])
@traceable(run_type="tool", name="chat_endpoint")
def chat():
    try:
        print(f"=== NEW CHAT REQUEST ===")

        # Handle JSON requests with image URLs
        data = request.get_json()
        user_input = data.get("message", "") if data else ""
        session_id = data.get("session_id") if data else None
        image_url = data.get("image_url") if data else None  # Get Cloudinary URL

        print(f"Message: '{user_input}'")
        print(f"Image URL: {image_url}")

        if not session_id:
            session_id = str(uuid.uuid4())

        if not user_input and not image_url:
            return jsonify({"error": "No message or image provided"}), 400

        # If image URL is provided, analyze it
        image_description = ""
        if image_url:
            try:
                print("=== ANALYZING IMAGE FROM URL ===")
                # Download image from Cloudinary URL for analysis
                import requests

                response = requests.get(image_url)
                image_data = response.content

                # Encode for Vision API
                base64_image = base64.b64encode(image_data).decode("utf-8")
                image_description = react_assistant.analyze_image(base64_image)
                print(f"Vision analysis complete: {len(image_description)} chars")

            except Exception as e:
                print(f"Image analysis error: {str(e)}")
                image_description = "Could not analyze image"

        # Combine input with image description
        if image_description:
            combined_input = (
                f"{user_input}\n\nUI Analysis: {image_description}"
                if user_input
                else f"Generate React code for this UI: {image_description}"
            )
        else:
            combined_input = user_input

        # Save user message to database
        user_message_data = {
            "session_id": session_id,
            "role": "user",
            "message": combined_input,
            "has_image": bool(image_url),
            "image_url": image_url,
            "created_at": datetime.datetime.now(),
        }
        messages_col.insert_one(user_message_data)

        # Generate response
        reply = react_assistant.generate_code(
            user_input=combined_input,
            image_description=image_description if image_description else None,
        )

        # Save assistant response
        assistant_message_data = {
            "session_id": session_id,
            "role": "assistant",
            "message": reply,
            "created_at": datetime.datetime.now(),
        }

        if image_url:
            assistant_message_data["references_image"] = image_url

        result = messages_col.insert_one(assistant_message_data)

        return (
            jsonify(
                {
                    "_id": str(result.inserted_id),
                    "session_id": session_id,
                    "role": "assistant",  # Make sure this is explicitly set
                    "message": reply,  # Make sure this contains only the assistant's response
                    "created_at": datetime.datetime.now().isoformat(),
                }
            ),
            201,
        )

    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({"error": str(e)}), 500


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
        print("=== IMAGE UPLOAD ENDPOINT ===")

        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files["image"]
        print(f"Uploading image: {image_file.filename}")

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
