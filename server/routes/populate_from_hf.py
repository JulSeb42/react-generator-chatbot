from flask import request, jsonify, Blueprint
from datasets import load_dataset
import openai
import datetime
import json
from utils.connect_db import base_api_url, snippets_col
from utils.pc_index import index

populate_bp = Blueprint("populate", __name__)

base_api_url = f"{base_api_url}/populate"


# @populate_bp.route(f"{base_api_url}/populate-from-hf", methods=["POST"])
# def populate_from_huggingface():
#     try:
#         # Load React components from HF dataset
#         dataset = load_dataset("cfahlgren1/react-code-instructions")

#         print(f"Dataset loaded. First item: {dataset['train'][0]}")

#         loaded_count = 0
#         for item in dataset["train"]:
#             try:
#                 # Extract messages (should be a list of conversation messages)
#                 messages = item.get("messages", [])

#                 if not messages:
#                     continue

#                 # Look for assistant messages containing React code
#                 for message in messages:
#                     if message.get("role") == "assistant":
#                         content = message.get("content", "")

#                         # Check if content contains React code (basic heuristics)
#                         if any(
#                             keyword in content.lower()
#                             for keyword in [
#                                 "import react",
#                                 "function component",
#                                 "export default",
#                                 "usestate",
#                                 "useeffect",
#                                 "jsx",
#                                 "tsx",
#                             ]
#                         ):
#                             # Extract metadata
#                             tags = []
#                             if item.get("recommended", False):
#                                 tags.append("recommended")
#                             if item.get("upvoted", False):
#                                 tags.append("upvoted")

#                             # Add model info as tag
#                             if item.get("model"):
#                                 tags.append(f"model:{item['model']}")

#                             # Store in MongoDB
#                             result = snippets_col.insert_one(
#                                 {
#                                     "text": content,
#                                     "tags": tags,
#                                     "original_dataset": "cfahlgren1/react-code-instructions",
#                                     "model": item.get("model"),
#                                     "recommended": item.get("recommended", False),
#                                     "upvoted": item.get("upvoted", False),
#                                     "created_at": datetime.datetime.utcnow(),
#                                     "updated_at": datetime.datetime.utcnow(),
#                                 }
#                             )

#                             snippet_id = str(result.inserted_id)

#                             # Generate embedding and store in Pinecone
#                             embedding = openai.Embedding.create(
#                                 input=content, model="text-embedding-ada-002"
#                             )["data"][0]["embedding"]

#                             index.upsert(
#                                 [
#                                     (
#                                         snippet_id,
#                                         embedding,
#                                         {
#                                             "text": content,
#                                             "tags": ",".join(tags),
#                                             "recommended": item.get(
#                                                 "recommended", False
#                                             ),
#                                             "upvoted": item.get("upvoted", False),
#                                         },
#                                     )
#                                 ]
#                             )

#                             loaded_count += 1
#                             print(f"Loaded snippet {loaded_count}")

#                             # Limit for testing (remove this later)
#                             if loaded_count >= 50:
#                                 break

#                 if loaded_count >= 50:  # Remove this limit later
#                     break

#             except Exception as item_error:
#                 print(f"Error processing item: {str(item_error)}")
#                 continue

#         return jsonify({"status": "success", "loaded": loaded_count})

#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return jsonify({"error": str(e)}), 500


# @populate_bp.route(f"{base_api_url}/populate-from-hf", methods=["POST"])
# def populate_from_huggingface():
#     try:
#         print("Starting populate from HuggingFace...")

#         # Use the original React dataset that we know works
#         print("Loading React code instructions dataset...")
#         dataset = load_dataset("cfahlgren1/react-code-instructions")
#         print(f"Dataset loaded. Total items: {len(dataset['train'])}")

#         loaded_count = 0
#         processed_count = 0

#         for item in dataset["train"]:
#             try:
#                 processed_count += 1
#                 if processed_count % 100 == 0:  # Progress update every 100 items
#                     print(
#                         f"Progress: Processed {processed_count}, Loaded {loaded_count}"
#                     )

#                 # Extract messages from the dataset
#                 messages = item.get("messages", [])
#                 if not messages:
#                     continue

#                 # Look for assistant messages containing React code
#                 for message in messages:
#                     if message.get("role") == "assistant":
#                         content = message.get("content", "")

#                         if not content or len(content) < 50:
#                             continue

#                         # Check if content contains React code
#                         react_keywords = [
#                             "import react",
#                             "from 'react'",
#                             "export default",
#                             "usestate",
#                             "useeffect",
#                             "jsx",
#                             "component",
#                         ]

#                         if any(
#                             keyword in content.lower() for keyword in react_keywords
#                         ):
#                             # Extract metadata
#                             tags = ["react"]
#                             if item.get("recommended", False):
#                                 tags.append("recommended")
#                             if item.get("upvoted", False):
#                                 tags.append("upvoted")
#                             if item.get("model"):
#                                 tags.append(f"model:{item['model']}")

#                             # Store in MongoDB
#                             try:
#                                 result = snippets_col.insert_one(
#                                     {
#                                         "text": content,
#                                         "tags": tags,
#                                         "original_dataset": "cfahlgren1/react-code-instructions",
#                                         "model": item.get("model"),
#                                         "recommended": item.get("recommended", False),
#                                         "upvoted": item.get("upvoted", False),
#                                         "created_at": datetime.datetime.utcnow(),
#                                         "updated_at": datetime.datetime.utcnow(),
#                                     }
#                                 )

#                                 snippet_id = str(result.inserted_id)

#                             except Exception as mongo_error:
#                                 print(f"MongoDB error: {str(mongo_error)}")
#                                 continue

#                             # Generate embedding and store in Pinecone
#                             try:
#                                 embedding_text = (
#                                     content[:4000] if len(content) > 4000 else content
#                                 )

#                                 embedding = openai.Embedding.create(
#                                     input=embedding_text,
#                                     model="text-embedding-ada-002",
#                                 )["data"][0]["embedding"]

#                                 index.upsert(
#                                     [
#                                         (
#                                             snippet_id,
#                                             embedding,
#                                             {
#                                                 "text": content[:500],
#                                                 "tags": ",".join(tags),
#                                                 "recommended": item.get(
#                                                     "recommended", False
#                                                 ),
#                                                 "upvoted": item.get("upvoted", False),
#                                             },
#                                         )
#                                     ]
#                                 )

#                             except Exception as pinecone_error:
#                                 print(f"Pinecone error: {str(pinecone_error)}")

#                             loaded_count += 1

#                             # INCREASED LIMIT - Change this number as needed
#                             if loaded_count >= 1000:  # Changed from 5 to 1000
#                                 print(f"Reached limit of {loaded_count} items")
#                                 break

#                 if loaded_count >= 1000:  # Changed from 5 to 1000
#                     break

#             except Exception as item_error:
#                 print(f"Error processing item {processed_count}: {str(item_error)}")
#                 continue

#         print(f"\n=== FINAL RESULTS ===")
#         print(f"Processed: {processed_count} items")
#         print(f"Loaded: {loaded_count} React components")

#         return jsonify(
#             {"status": "success", "loaded": loaded_count, "processed": processed_count}
#         )

#     except Exception as e:
#         error_msg = f"Main error: {str(e)}"
#         print(f"Error: {error_msg}")
#         import traceback

#         traceback.print_exc()
#         return jsonify({"error": error_msg}), 500


@populate_bp.route(f"{base_api_url}/populate-from-hf", methods=["POST"])
def populate_from_huggingface():
    try:
        print("Starting populate from HuggingFace...")

        # Load the React dataset
        print("Loading React code instructions dataset...")
        dataset = load_dataset("cfahlgren1/react-code-instructions")
        print(f"Dataset loaded. Total items: {len(dataset['train'])}")

        loaded_count = 0
        processed_count = 0
        pinecone_batch = []  # Batch upserts for better performance

        for item in dataset["train"]:
            try:
                processed_count += 1
                if processed_count % 100 == 0:
                    print(
                        f"Progress: Processed {processed_count}, Loaded {loaded_count}"
                    )

                # Extract messages from the dataset
                messages = item.get("messages", [])
                if not messages:
                    continue

                # Look for assistant messages containing React code
                for message in messages:
                    if message.get("role") == "assistant":
                        content = message.get("content", "")

                        if not content or len(content) < 50:
                            continue

                        # Check if content contains React code
                        react_keywords = [
                            "import react",
                            "from 'react'",
                            "export default",
                            "usestate",
                            "useeffect",
                            "jsx",
                            "component",
                            "function",
                            "const",
                            "=>",
                            "return",
                        ]

                        if any(
                            keyword in content.lower() for keyword in react_keywords
                        ):
                            # Extract metadata
                            tags = ["react"]
                            if item.get("recommended", False):
                                tags.append("recommended")
                            if item.get("upvoted", False):
                                tags.append("upvoted")
                            if item.get("model"):
                                tags.append(f"model:{item['model']}")

                            # Store in MongoDB
                            try:
                                result = snippets_col.insert_one(
                                    {
                                        "text": content,
                                        "tags": tags,
                                        "original_dataset": "cfahlgren1/react-code-instructions",
                                        "model": item.get("model"),
                                        "recommended": item.get("recommended", False),
                                        "upvoted": item.get("upvoted", False),
                                        "created_at": datetime.datetime.utcnow(),
                                        "updated_at": datetime.datetime.utcnow(),
                                    }
                                )
                                snippet_id = str(result.inserted_id)
                            except Exception as mongo_error:
                                print(f"MongoDB error: {str(mongo_error)}")
                                continue

                            # Generate embedding
                            try:
                                # Limit text length for embedding API
                                embedding_text = (
                                    content[:8000] if len(content) > 8000 else content
                                )

                                embedding = openai.Embedding.create(
                                    input=embedding_text,
                                    model="text-embedding-ada-002",
                                )["data"][0]["embedding"]

                                # Add to batch for Pinecone
                                pinecone_batch.append(
                                    (
                                        snippet_id,
                                        embedding,
                                        {
                                            "text": content[
                                                :1000
                                            ],  # Truncate for metadata
                                            "tags": ",".join(tags),
                                            "recommended": item.get(
                                                "recommended", False
                                            ),
                                            "upvoted": item.get("upvoted", False),
                                            "model": item.get("model", "unknown"),
                                            "dataset": "cfahlgren1/react-code-instructions",
                                        },
                                    )
                                )

                                loaded_count += 1

                                # Batch upsert to Pinecone every 100 items
                                if len(pinecone_batch) >= 100:
                                    print(
                                        f"Upserting batch of {len(pinecone_batch)} to Pinecone..."
                                    )
                                    index.upsert(pinecone_batch)
                                    pinecone_batch = []  # Clear batch

                            except Exception as embedding_error:
                                print(
                                    f"Embedding/Pinecone error: {str(embedding_error)}"
                                )
                                continue

                            # Stop at limit
                            if loaded_count >= 1000:
                                print(f"Reached limit of {loaded_count} items")
                                break

                if loaded_count >= 1000:
                    break

            except Exception as item_error:
                print(f"Error processing item {processed_count}: {str(item_error)}")
                continue

        # Upload remaining batch to Pinecone
        if pinecone_batch:
            print(f"Upserting final batch of {len(pinecone_batch)} to Pinecone...")
            index.upsert(pinecone_batch)

        print(f"\n=== FINAL RESULTS ===")
        print(f"Processed: {processed_count} items")
        print(f"Loaded: {loaded_count} React components")
        print(f"Successfully populated Pinecone with {loaded_count} embeddings")

        return jsonify(
            {
                "status": "success",
                "loaded": loaded_count,
                "processed": processed_count,
                "pinecone_populated": True,
            }
        )

    except Exception as e:
        error_msg = f"Main error: {str(e)}"
        print(f"Error: {error_msg}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": error_msg}), 500
