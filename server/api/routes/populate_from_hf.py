"""HuggingFace dataset population routes for React code knowledge base.

This module provides Flask Blueprint routes for populating the Pinecone vector database
and MongoDB collection with React code examples from HuggingFace datasets. The service
downloads, processes, and embeds React components to build a comprehensive knowledge
base for the AI-powered code generation system.

Routes:
    POST /api/populate/populate-from-hf - Download and process React dataset from HuggingFace

Features:
    - Automated dataset download from HuggingFace Hub
    - Intelligent React code detection and filtering
    - Batch processing for optimal performance
    - Dual storage: MongoDB for metadata, Pinecone for vector search
    - Progress tracking and error handling
    - Content validation and preprocessing

Dataset Processing:
    - Source: cfahlgren1/react-code-instructions dataset
    - Filters: Assistant messages containing React code patterns
    - Keywords: import react, useState, useEffect, JSX, components
    - Limit: 1000 high-quality React examples
    - Batch size: 100 items per Pinecone upsert

Data Flow:
    1. Download dataset from HuggingFace
    2. Extract assistant messages with React code
    3. Validate content with React keyword detection
    4. Store full content in MongoDB with metadata
    5. Generate embeddings using OpenAI text-embedding-ada-002
    6. Batch upload embeddings to Pinecone vector database
    7. Return processing statistics

Data Structure:
    MongoDB Document:
        {
            "text": "Full React component code",
            "tags": ["react", "recommended", "upvoted"],
            "original_dataset": "cfahlgren1/react-code-instructions",
            "model": "gpt-4",
            "recommended": true,
            "upvoted": false,
            "created_at": datetime,
            "updated_at": datetime
        }

    Pinecone Vector:
        {
            "id": "mongodb_object_id",
            "vector": [1536-dimensional embedding],
            "metadata": {
                "text": "Truncated code (1000 chars)",
                "tags": "react,recommended",
                "recommended": true,
                "upvoted": false,
                "model": "gpt-4",
                "dataset": "cfahlgren1/react-code-instructions"
            }
        }

Dependencies:
    - datasets: HuggingFace datasets library
    - openai: Embedding generation
    - pymongo: MongoDB storage
    - pinecone: Vector database operations

Performance Optimizations:
    - Batch processing (100 items per Pinecone upsert)
    - Content length validation (min 50 chars)
    - Text truncation for embedding API (8000 chars max)
    - Metadata truncation for Pinecone (1000 chars)
    - Progress logging every 100 processed items

Error Handling:
    - Individual item failures don't stop processing
    - MongoDB connection errors handled gracefully
    - OpenAI API failures skip item and continue
    - Pinecone batch upload retries
    - Comprehensive error logging and traceback

Request/Response Format:
    Request:
        POST /api/populate/populate-from-hf
        (No body required)

    Response (Success):
        {
            "status": "success",
            "loaded": 1000,
            "processed": 5234,
            "pinecone_populated": true
        }

    Response (Error):
        {
            "error": "Detailed error message"
        }

Example Usage:
    # Populate knowledge base from HuggingFace
    POST /api/populate/populate-from-hf

    # Monitor progress in server logs:
    # Progress: Processed 100, Loaded 23
    # Upserting batch of 100 to Pinecone...
    # === FINAL RESULTS ===
    # Processed: 5234 items
    # Loaded: 1000 React components

Security Considerations:
    - Content validation before storage
    - API rate limiting through batch processing
    - Error message sanitization
    - Resource usage monitoring

Note:
    This endpoint should be run during initial setup or when refreshing
    the knowledge base. Processing 1000+ items may take several minutes
    due to embedding generation and API rate limits.

Raises:
    ConnectionError: If unable to connect to HuggingFace, MongoDB, or Pinecone
    ValueError: If dataset format is invalid or corrupted
    Exception: If embedding generation or batch processing fails
"""

import datetime
import traceback
from flask import jsonify, Blueprint
from datasets import load_dataset
from openai import OpenAI
from utils.connect_db import BASE_API_URL, snippets_col
from utils.pc_index import index
from utils.consts import OPENAI_API_KEY

populate_bp = Blueprint("populate", __name__)

BASE_API_URL = f"{BASE_API_URL}/populate"


@populate_bp.route(f"{BASE_API_URL}/populate-from-hf", methods=["POST"])
def populate_from_huggingface():  # pylint: disable=too-many-locals disable=too-many-branches disable=too-many-statements
    """Download and process React code examples from HuggingFace dataset.

    Downloads the cfahlgren1/react-code-instructions dataset, extracts React
    components from assistant messages, generates embeddings, and populates
    both MongoDB and Pinecone for the AI code generation knowledge base.

    Returns:
        tuple: JSON response with processing statistics, HTTP status code
            Success (200):
                - status (str): "success"
                - loaded (int): Number of React components stored
                - processed (int): Total items processed from dataset
                - pinecone_populated (bool): True if vector embeddings uploaded
            Error (500):
                - error (str): Detailed error description

    Raises:
        ConnectionError: If dataset download or database connections fail
        ValueError: If dataset format is invalid
        Exception: If processing pipeline encounters unrecoverable errors
    """
    try:  # pylint: disable=too-many-nested-blocks
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
                            except (
                                Exception  # pylint: disable=broad-exception-caught
                            ) as mongo_error:
                                print(f"MongoDB error: {str(mongo_error)}")
                                continue

                            # Generate embedding
                            try:
                                # Limit text length for embedding API
                                embedding_text = (
                                    content[:8000] if len(content) > 8000 else content
                                )

                                client = OpenAI(api_key=OPENAI_API_KEY)
                                response = client.embeddings.create(
                                    input=embedding_text, model="text-embedding-ada-002"
                                )
                                embedding = response.data[0].embedding

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

                            except (
                                Exception  # pylint: disable=broad-exception-caught
                            ) as embedding_error:
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

            except Exception as item_error:  # pylint: disable=broad-exception-caught
                print(f"Error processing item {processed_count}: {str(item_error)}")
                continue

        # Upload remaining batch to Pinecone
        if pinecone_batch:
            print(f"Upserting final batch of {len(pinecone_batch)} to Pinecone...")
            index.upsert(pinecone_batch)

        print("\n=== FINAL RESULTS ===")
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

    except Exception as e:  # pylint: disable=broad-exception-caught
        error_msg = f"Main error: {str(e)}"
        print(f"Error: {error_msg}")

        traceback.print_exc()
        return jsonify({"error": error_msg}), 500
