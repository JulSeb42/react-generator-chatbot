from flask import Blueprint, jsonify, request
import json
import uuid
import datetime
import openai
from utils.connect_db import base_api_url, messages_col, snippets_col
from utils.pc_index import index

chat_bp = Blueprint("chat", __name__)
base_api_url = f"{base_api_url}/chat"


@chat_bp.route(f"{base_api_url}/chats", methods=["GET"])
def get_all_chats():
    chats = messages_col.find()
    all_chats = []
    for chat in chats:
        chat["_id"] = str(chat["_id"])
        all_chats.append(chat)
    return all_chats, 201


@chat_bp.route(f"{base_api_url}/new-chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message")
    session_id = data.get("session_id")

    if not session_id:
        session_id = str(uuid.uuid4())

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    # Save user message
    messages_col.insert_one(
        {"session_id": session_id, "role": "user", "message": user_input}
    )

    # Embed user input and query Pinecone
    embedding = openai.Embedding.create(
        input=user_input, model="text-embedding-ada-002"
    )["data"][0]["embedding"]

    pinecone_result = index.query(vector=embedding, top_k=3, include_metadata=True)

    # Build context from Pinecone matches
    context_snippets = [
        match["metadata"]["text"]
        for match in pinecone_result.get("matches", [])
        if "text" in match["metadata"]
    ]
    context = "\n\n".join(context_snippets)

    # Build messages for OpenAI
    system_prompt = (
        "You are a senior React developer. Generate high-quality React code based on user requests.\n"
        "Use functional components, hooks, and modern best practices. If relevant, include helpful comments."
    )

    messages = [
        {"role": "system", "content": system_prompt},
    ]

    if context:
        messages.append(
            {
                "role": "system",
                "content": f"Here are some related examples:\n\n{context}",
            }
        )

    messages.append({"role": "user", "content": user_input})

    # Get completion from OpenAI
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4", messages=messages, temperature=0.3
        )
        reply = completion["choices"][0]["message"]["content"]

        # Save assistant reply
        result = messages_col.insert_one(
            {
                "session_id": session_id,
                "role": "assistant",
                "message": reply,
                "created_at": datetime.datetime.now(),
            }
        )
        assistant_message_id = str(result.inserted_id)

        return (
            jsonify(
                {
                    "_id": assistant_message_id,
                    "session_id": session_id,
                    "role": "assistant",
                    "message": reply,
                    "created_at": datetime.datetime.now(),
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# @chat_bp.route(f"{base_api_url}/new-message/<session_id>")
# def new_message(session_id):
#     data = request.json()
#     user_input = data.get("message")
#     session_id = data.get("session_id")

#     if not user_input:
#         return jsonify({"error": "No message provided"}), 400

#     return


# @chat_bp.route(f"{base_api_url}/new-message/<session_id>")
# def new_message(session_id):
#     return


@chat_bp.route(f"{base_api_url}/messages/<session_id>", methods=["GET"])
def get_session_messages(session_id):
    res = messages_col.find({"session_id": str(session_id)})
    messages = list(res)
    for message in messages:
        message["_id"] = str(message["_id"])
    return jsonify(messages), 201


# @chat_bp.route(f"{base_api_url}/messages/<session_id>", methods=["GET"])
# def get_session_messages(session_id):
#     from utils.connect_db import get_db_connection

#     with get_db_connection() as conn:
#         cursor = conn.execute(
#             "SELECT id, session_id, role, message, created_at FROM messages WHERE session_id = ? ORDER BY created_at",
#             (session_id,),
#         )
#         messages = []
#         for row in cursor.fetchall():
#             messages.append(
#                 {
#                     "id": row["id"],
#                     "session_id": row["session_id"],
#                     "role": row["role"],
#                     "message": row["message"],
#                     "created_at": row["created_at"],
#                 }
#             )

#     return jsonify(messages), 200


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
