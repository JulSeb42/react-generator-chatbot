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
        print(f"=== NEW CHAT REQUEST START ===")
        print(f"Request method: {request.method}")
        print(f"Request content type: {request.content_type}")

        # Step 1: Parse request data
        try:
            data = request.get_json()
            print(f"✅ Step 1: JSON parsed successfully: {data}")
        except Exception as json_error:
            print(f"❌ Step 1: JSON parsing failed: {json_error}")
            return jsonify({"error": f"Invalid JSON: {str(json_error)}"}), 400

        user_input = data.get("message", "") if data else ""
        session_id = data.get("session_id") if data else None
        image_url = data.get("image_url") if data else None

        print(
            f"✅ Step 2: Extracted data - User: '{user_input}', Session: {session_id}, Image: {image_url}"
        )

        # Step 3: Generate session ID if needed
        if not session_id:
            session_id = str(uuid.uuid4())
            print(f"✅ Step 3: Generated session ID: {session_id}")

        if not user_input and not image_url:
            print("❌ Step 4: No message or image provided")
            return jsonify({"error": "No message or image provided"}), 400

        print(f"✅ Step 4: Input validation passed")

        # Step 5: Image analysis (if image provided)
        image_description = ""
        if image_url:
            try:
                print("✅ Step 5a: Starting image analysis...")
                import requests

                print("✅ Step 5b: Downloading image...")
                response = requests.get(image_url, timeout=10)  # Reduced timeout
                response.raise_for_status()
                image_data = response.content
                print(f"✅ Step 5c: Image downloaded, size: {len(image_data)} bytes")

                base64_image = base64.b64encode(image_data).decode("utf-8")
                print(
                    f"✅ Step 5d: Image encoded, base64 length: {len(base64_image)} chars"
                )

                print("✅ Step 5e: Calling Vision API...")
                try:
                    image_description = react_assistant.analyze_image(base64_image)
                    print(
                        f"✅ Step 5f: Vision analysis complete: {len(image_description)} chars"
                    )
                except Exception as vision_error:
                    print(f"❌ Step 5f: Vision API error: {str(vision_error)}")
                    image_description = "Image analysis failed"

            except Exception as image_error:
                print(f"❌ Step 5: Image processing error: {str(image_error)}")
                image_description = "Image processing failed"
        else:
            print(f"✅ Step 5: No image to process")

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

            print(f"✅ Step 6: AI input prepared, length: {len(ai_input)} chars")
        except Exception as input_error:
            print(f"❌ Step 6: AI input preparation error: {str(input_error)}")
            return (
                jsonify({"error": f"Input preparation failed: {str(input_error)}"}),
                500,
            )

        # Step 7: Save user message
        try:
            print("✅ Step 7a: Saving user message...")
            user_message_data = {
                "session_id": session_id,
                "role": "user",
                "message": user_input,
                "has_image": bool(image_url),
                "image_url": image_url,
                "created_at": datetime.datetime.now(),
            }
            print(f"✅ Step 7b: User message data prepared: {user_message_data}")

            messages_col.insert_one(user_message_data)
            print(f"✅ Step 7c: User message saved to database")
        except Exception as save_error:
            print(f"❌ Step 7: User message save error: {str(save_error)}")
            return (
                jsonify({"error": f"Failed to save user message: {str(save_error)}"}),
                500,
            )
        try:
            print("✅ Step 8a: Generating AI response...")
            reply = react_assistant.generate_code(
                user_input=ai_input,
                image_description=image_description if image_description and "failed" not in image_description.lower() else None,
            )
            print(f"✅ Step 8b: AI response generated, length: {len(reply)} chars")
        except Exception as ai_error:
            print(f"❌ Step 8: AI generation error: {str(ai_error)}")
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
            
            export default Button;"""

        # Step 9: Save assistant response
        try:
            print("✅ Step 9a: Saving assistant response...")
            assistant_message_data = {
                "session_id": session_id,
                "role": "assistant",
                "message": reply,
                "created_at": datetime.datetime.now(),
            }

            if image_url:
                assistant_message_data["references_image"] = image_url

            print(f"✅ Step 9b: Assistant message data prepared")
            result = messages_col.insert_one(assistant_message_data)
            print(f"✅ Step 9c: Assistant message saved with ID: {result.inserted_id}")
        except Exception as save_error:
            print(f"❌ Step 9: Assistant message save error: {str(save_error)}")
            return (
                jsonify(
                    {"error": f"Failed to save assistant message: {str(save_error)}"}
                ),
                500,
            )

        # Step 10: Prepare response
        try:
            print("✅ Step 10a: Preparing response...")
            response_data = {
                "_id": str(result.inserted_id),
                "session_id": session_id,
                "role": "assistant",
                "message": reply,
                "created_at": datetime.datetime.now().isoformat(),
            }
            print(f"✅ Step 10b: Response data prepared: {list(response_data.keys())}")

            print(f"✅ Step 10c: Returning successful response")
            return jsonify(response_data), 201

        except Exception as response_error:
            print(f"❌ Step 10: Response preparation error: {str(response_error)}")
            return (
                jsonify(
                    {"error": f"Failed to prepare response: {str(response_error)}"}
                ),
                500,
            )

    except Exception as e:
        print(f"❌ UNHANDLED ERROR IN CHAT ENDPOINT")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        import traceback

        print(f"Full traceback:")
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


@chat_bp.route(f"{base_api_url}/test-vision", methods=["POST"])
def test_vision():
    """Test vision API with minimal payload"""
    try:
        # Simple test with a small base64 image
        test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

        response = react_assistant.analyze_image(test_image)
        return jsonify({"success": True, "response": response})
    except Exception as e:
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


@chat_bp.route(f"{base_api_url}/test-components", methods=["GET", "POST"])
def test_components():
    results = {}

    # Test database
    try:
        test_doc = messages_col.find_one()
        results["database"] = "✅ Connected"
    except Exception as e:
        results["database"] = f"❌ Error: {str(e)}"

    # Test react_assistant
    try:
        test_response = react_assistant.generate_code("test input")
        results["react_assistant"] = (
            f"✅ Working (response length: {len(test_response)})"
        )
    except Exception as e:
        results["react_assistant"] = f"❌ Error: {str(e)}"

    # Test cloudinary_service
    try:
        from utils.cloudinary_service import cloudinary_service

        results["cloudinary_service"] = "✅ Imported successfully"
    except Exception as e:
        results["cloudinary_service"] = f"❌ Error: {str(e)}"

    return jsonify(results)


@chat_bp.route(f"{base_api_url}/test-db", methods=["GET"])
def test_db():
    try:
        test_doc = messages_col.find_one()
        return jsonify({"status": "✅ Database connected"})
    except Exception as e:
        return jsonify({"status": f"❌ Database error: {str(e)}"}), 500


@chat_bp.route(f"{base_api_url}/test-ai", methods=["GET"])
def test_ai():
    try:
        test_response = react_assistant.generate_code(
            "Create a simple button component"
        )
        return jsonify(
            {
                "status": "✅ AI working",
                "response_length": len(test_response),
                "sample": (
                    test_response[:200] + "..."
                    if len(test_response) > 200
                    else test_response
                ),
            }
        )
    except Exception as e:
        return jsonify({"status": f"❌ AI error: {str(e)}"}), 500


@chat_bp.route(f"{base_api_url}/test-cloudinary", methods=["GET"])
def test_cloudinary():
    try:
        from utils.cloudinary_service import cloudinary_service

        return jsonify({"status": "✅ Cloudinary service imported"})
    except Exception as e:
        return jsonify({"status": f"❌ Cloudinary error: {str(e)}"}), 500
