from flask import Blueprint, jsonify, request
import uuid
import datetime
import openai
from langsmith import traceable
import base64
from utils.connect_db import base_api_url, messages_col, snippets_col
from utils.pc_index import index
from utils.langchain_service import react_assistant

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

        # Handle both JSON and FormData
        if request.content_type and "multipart/form-data" in request.content_type:
            user_input = request.form.get("message", "")
            session_id = request.form.get("session_id")
            image_file = request.files.get("image")
            print(
                f"FormData received - Message: '{user_input}', Image: {image_file is not None}"
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

        # Process image if provided using LangChain
        image_description = ""
        if image_file:
            print(f"Processing image: {image_file.filename}")
            try:
                # Read and encode image
                image_data = image_file.read()
                base64_image = base64.b64encode(image_data).decode("utf-8")
                print(
                    f"Image encoded successfully, size: {len(base64_image)} characters"
                )

                # Use LangChain for image analysis
                print("Calling LangChain Vision analysis...")
                image_description = react_assistant.analyze_image(base64_image)
                print(
                    f"LangChain Vision SUCCESS! Response length: {len(image_description)} characters"
                )

            except Exception as e:
                print(f"Vision analysis error: {str(e)}")
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

        # Save user message to database
        messages_col.insert_one(
            {
                "session_id": session_id,
                "role": "user",
                "message": combined_input,
                "has_image": bool(image_file),
                "created_at": datetime.datetime.now(),
            }
        )

        # Generate response using LangChain RAG chain
        print("Generating response with LangChain...")
        reply = react_assistant.generate_code(
            user_input=user_input if not image_description else combined_input,
            image_description=image_description if image_description else None,
        )

        print(f"LangChain response generated, length: {len(reply)} characters")

        # Save assistant reply to database
        result = messages_col.insert_one(
            {
                "session_id": session_id,
                "role": "assistant",
                "message": reply,
                "created_at": datetime.datetime.now(),
            }
        )

        # Return the response
        return (
            jsonify(
                {
                    "_id": str(result.inserted_id),
                    "session_id": session_id,
                    "role": "assistant",
                    "message": reply,
                    "created_at": datetime.datetime.now().isoformat(),
                }
            ),
            201,
        )

    except Exception as e:
        print(f"Chat error: {str(e)}")
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
