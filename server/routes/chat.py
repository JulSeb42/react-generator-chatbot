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
        print(f"Request content type: {request.content_type}")
        print(f"Request files: {list(request.files.keys())}")
        print(f"Request form: {dict(request.form)}")

        # Check if cloudinary_service is available
        print(f"Cloudinary service available: {cloudinary_service is not None}")

        # Handle both JSON and FormData
        if request.content_type and "multipart/form-data" in request.content_type:
            user_input = request.form.get("message", "")
            session_id = request.form.get("session_id")
            image_file = request.files.get("image")
            print(
                f"FormData received - Message: '{user_input}', Image: {image_file is not None}"
            )
            if image_file:
                print(
                    f"Image details - Filename: {image_file.filename}, Content-Type: {image_file.content_type}"
                )
        else:
            data = request.get_json()
            user_input = data.get("message", "") if data else ""
            session_id = data.get("session_id") if data else None
            image_file = None
            print(f"JSON received - Message: '{user_input}'")

        if not session_id:
            session_id = str(uuid.uuid4())

        if not user_input and not image_file:
            return jsonify({"error": "No message or image provided"}), 400

        # Process image if provided
        image_description = ""
        image_url = None
        cloudinary_public_id = None

        if image_file:
            print(f"Processing image: {image_file.filename}")
            print(f"Image file stream position: {image_file.tell()}")

            try:
                # Reset file pointer to beginning
                image_file.seek(0)

                # Read image data
                image_data = image_file.read()
                print(f"Image data read, size: {len(image_data)} bytes")

                if len(image_data) == 0:
                    print("ERROR: Image data is empty!")
                    return jsonify({"error": "Image file is empty"}), 400

                # Upload to Cloudinary first
                print("=== CALLING CLOUDINARY SERVICE ===")
                cloudinary_result = cloudinary_service.upload_image(
                    file_data=image_data,
                    filename=image_file.filename or "ui_mockup",
                    folder="ui-mockups",
                )

                print(f"=== CLOUDINARY SERVICE RESULT ===")
                print(f"Result: {cloudinary_result}")

                if cloudinary_result["success"]:
                    image_url = cloudinary_result["url"]
                    cloudinary_public_id = cloudinary_result["public_id"]
                    print(f"Cloudinary upload successful: {image_url}")
                else:
                    print(f"Cloudinary upload failed: {cloudinary_result.get('error')}")
                    return (
                        jsonify(
                            {
                                "error": f"Failed to upload image: {cloudinary_result.get('error')}"
                            }
                        ),
                        500,
                    )

                # Encode for OpenAI Vision API (reset file pointer first)
                image_file.seek(0)
                image_data_for_vision = image_file.read()
                base64_image = base64.b64encode(image_data_for_vision).decode("utf-8")
                print(
                    f"Image encoded for Vision API, size: {len(base64_image)} characters"
                )

                # Use LangChain for image analysis
                print("Calling LangChain Vision analysis...")
                image_description = react_assistant.analyze_image(base64_image)
                print(
                    f"LangChain Vision SUCCESS! Response length: {len(image_description)} characters"
                )

            except Exception as e:
                print(f"Image processing error: {str(e)}")
                import traceback

                traceback.print_exc()
                # Clean up Cloudinary image if vision analysis fails
                if cloudinary_public_id:
                    print(f"Cleaning up Cloudinary image: {cloudinary_public_id}")
                    cloudinary_service.delete_image(cloudinary_public_id)
                image_description = (
                    f"Error analyzing image: {str(e)}. Please describe the UI manually."
                )

        # Combine user input with image description
        if image_description:
            combined_input = (
                f"{user_input}\n\nUI Analysis: {image_description}"
                if user_input
                else f"Generate React code for this UI: {image_description}"
            )
        else:
            combined_input = user_input

        print(f"Final combined input: {combined_input[:300]}...")

        # Save user message to database (including image info)
        user_message_data = {
            "session_id": session_id,
            "role": "user",
            "message": combined_input,
            "has_image": bool(image_file),
            "created_at": datetime.datetime.now(),
        }

        # Add image data if available
        if image_url:
            user_message_data.update(
                {
                    "image_url": image_url,
                    "cloudinary_public_id": cloudinary_public_id,
                    "original_filename": image_file.filename if image_file else None,
                }
            )

        print(f"Saving user message to database: {user_message_data}")
        messages_col.insert_one(user_message_data)

        # Generate response using LangChain
        print("Generating response with LangChain...")
        reply = react_assistant.generate_code(
            user_input=user_input if not image_description else combined_input,
            image_description=image_description if image_description else None,
        )

        print(f"LangChain response generated, length: {len(reply)} characters")

        # Save assistant reply to database
        assistant_message_data = {
            "session_id": session_id,
            "role": "assistant",
            "message": reply,
            "created_at": datetime.datetime.now(),
        }

        # Reference the image if it was part of the conversation
        if image_url:
            assistant_message_data["references_image"] = image_url

        print(f"Saving assistant message to database: {assistant_message_data}")
        result = messages_col.insert_one(assistant_message_data)

        # Return the response
        response_data = {
            "_id": str(result.inserted_id),
            "session_id": session_id,
            "role": "assistant",
            "message": reply,
            "created_at": datetime.datetime.now().isoformat(),
        }

        # Include image URL in response if available
        if image_url:
            response_data["image_url"] = image_url
            response_data["cloudinary_public_id"] = cloudinary_public_id

        print(f"Returning response: {response_data}")
        return jsonify(response_data), 201

    except Exception as e:
        print(f"=== CHAT ERROR ===")
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@chat_bp.route(f"{base_api_url}/test-cloudinary", methods=["POST"])
def test_cloudinary():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image provided"}), 400

        image_file = request.files["image"]
        image_data = image_file.read()

        result = cloudinary_service.upload_image(
            file_data=image_data, filename="test_image", folder="test"
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route(f"{base_api_url}/test-image-upload", methods=["POST"])
def test_image_upload():
    try:
        print("=== TEST IMAGE UPLOAD ENDPOINT ===")
        print(f"Content type: {request.content_type}")
        print(f"Files keys: {list(request.files.keys())}")
        print(f"Form keys: {list(request.form.keys())}")

        # Debug all received data
        for key in request.files:
            file = request.files[key]
            print(f"File '{key}': {file.filename}, {file.content_type}")

        for key in request.form:
            print(f"Form '{key}': {request.form[key]}")

        if "image" not in request.files:
            print("ERROR: No 'image' in request.files")
            return (
                jsonify(
                    {
                        "error": "No image file found",
                        "received_files": list(request.files.keys()),
                        "received_form": list(request.form.keys()),
                    }
                ),
                400,
            )

        image_file = request.files["image"]
        print(f"Image file received: {image_file.filename}")
        print(f"Image content type: {image_file.content_type}")
        print(f"Image content length: {image_file.content_length}")

        # Try to read a small amount of data to verify file is not empty
        current_pos = image_file.tell()
        image_file.seek(0, 2)  # Seek to end
        file_size = image_file.tell()
        image_file.seek(current_pos)  # Reset position
        print(f"Actual file size: {file_size} bytes")

        if file_size == 0:
            return jsonify({"error": "Image file is empty"}), 400

        # Success response
        return (
            jsonify(
                {
                    "success": True,
                    "filename": image_file.filename,
                    "content_type": image_file.content_type,
                    "file_size": file_size,
                    "message": "File received successfully",
                    "form_data": dict(request.form),
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Test endpoint error: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# Add this test route to your chat.py
@chat_bp.route(f"{base_api_url}/test-cloudinary-upload", methods=["POST"])
def test_cloudinary_upload():
    try:
        print("=== CLOUDINARY TEST ENDPOINT ===")

        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files["image"]
        print(f"Received file: {image_file.filename}")

        # Reset file pointer
        image_file.seek(0)
        image_data = image_file.read()
        print(f"File size: {len(image_data)} bytes")

        # Test Cloudinary upload
        result = cloudinary_service.upload_image(
            file_data=image_data, filename="test_upload", folder="test"
        )

        return (
            jsonify(
                {
                    "cloudinary_result": result,
                    "file_info": {
                        "filename": image_file.filename,
                        "size": len(image_data),
                        "content_type": image_file.content_type,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Test endpoint error: {str(e)}")
        import traceback

        traceback.print_exc()
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


# @chat_bp.route(f"{base_api_url}/add-snippet", methods=["POST"])
# def add_snippet():
#     data = request.get_json()
#     text = data["text"]
#     tags = data.get("tags", [])

#     from utils.connect_db import get_db_connection

#     # Store in SQLite DB
#     with get_db_connection() as conn:
#         cursor = conn.execute(
#             "INSERT INTO snippets (content, tags) VALUES (?, ?)", (text, ",".join(tags))
#         )
#         conn.commit()
#         snippet_id = cursor.lastrowid

#     # Generate and upload to Pinecone
#     embedding = openai.Embedding.create(input=text, model="text-embedding-ada-002")[
#         "data"
#     ][0]["embedding"]
#     index.upsert([(str(snippet_id), embedding, {"text": text, "tags": ",".join(tags)})])

#     return jsonify({"status": "added", "id": snippet_id})
