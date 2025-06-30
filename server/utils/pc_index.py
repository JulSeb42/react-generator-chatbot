"""Pinecone vector database connection module.

This module establishes a connection to the Pinecone vector database and provides
a globally accessible index instance for the Ironhack Final Project.

The module initializes a Pinecone client using the API key from environment variables
and connects to the 'ironhack-final-project' index, which stores embedded React code
examples and UI component patterns for semantic similarity search.

Globals:
    pc (Pinecone): Initialized Pinecone client instance
    index (Pinecone.Index): Connected Pinecone index for vector operations

Usage:
    from utils.pc_index import index

    # Perform vector similarity search
    results = index.query(vector=embedding_vector, top_k=5)

    # Upsert new vectors
    index.upsert(vectors=[("id", embedding, metadata)])

Dependencies:
    - pinecone: Pinecone Python client library
    - PINECONE_API_KEY: API key from environment variables

Raises:
    ValueError: If PINECONE_API_KEY is invalid or missing
    ConnectionError: If unable to connect to Pinecone service
    KeyError: If the specified index 'ironhack-final-project' doesn't exist

Note:
    This module is imported at application startup and creates a persistent
    connection to the Pinecone vector database for use throughout the application.
"""

from pinecone import Pinecone
from utils.consts import PINECONE_API_KEY

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("ironhack-final-project")
