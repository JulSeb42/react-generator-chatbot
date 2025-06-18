from flask import Blueprint, jsonify, request
import uuid
import openai
from utils.consts import base_api_url
from utils.connect_db import messages_col
from utils.pc_index import index

chat_bp = Blueprint("chat", __name__)
base_api_url = f"{base_api_url}/chat"


@chat_bp.route(f"{base_api_url}", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message")
    session_id = data.get("session_id", str(uuid.uuid4()))

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
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Save assistant reply
    messages_col.insert_one(
        {"session_id": session_id, "role": "assistant", "message": reply}
    )

    return jsonify({"reply": reply, "session_id": session_id})


@chat_bp.route(f"{base_api_url}/chats", methods=["GET"])
def get_all_chats():
    chats = messages_col.find()
    all_chats = []
    for chat in chats:
        chat["_id"] = str(chat["_id"])
        all_chats.append(chat)
    return all_chats
