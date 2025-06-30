"""Pinecone database population utility for React code examples.

This script initializes and populates the Pinecone vector database with embedded
React code snippets for use in the AI-powered code generation system. The script
creates the index if it doesn't exist and uploads sample React components with
their corresponding vector embeddings for semantic similarity search.

The populated database serves as a knowledge base for the ReactCodeAssistant,
enabling it to retrieve contextually relevant code examples when generating
new React components based on user requests.

Features:
    - Automatic Pinecone index creation with optimal configuration
    - React code snippet embedding using OpenAI's text-embedding-ada-002
    - Batch upload of code examples with metadata tags
    - Serverless index configuration for cost-effective scaling

Index Configuration:
    - Name: ironhack-final-project
    - Dimension: 1536 (matching OpenAI embedding model)
    - Metric: cosine similarity
    - Cloud: AWS (us-east-1 region)
    - Type: Serverless for automatic scaling

Code Examples Included:
    - Contact forms with React hooks
    - API data fetching with useEffect
    - Controlled form components
    - State management patterns

Dependencies:
    - openai: For generating text embeddings
    - pinecone: Vector database client
    - OPENAI_API_KEY: Required environment variable
    - PINECONE_API_KEY: Required environment variable

Usage:
    python utils/populate_pinecone.py

Example:
    # Run the script to populate the database
    cd server
    python utils/populate_pinecone.py

    # Output: ✅ Snippets uploaded to Pinecone.

Data Structure:
    Each code snippet is stored with:
    - id (str): Unique identifier for the code example
    - vector (list): 1536-dimensional embedding
    - metadata (dict): Contains 'text' and 'tags' fields

Note:
    This script should be run once during initial setup or when adding
    new code examples to the knowledge base. Running multiple times will
    overwrite existing entries with the same IDs.

Raises:
    ConnectionError: If unable to connect to Pinecone service
    ValueError: If OpenAI API key is invalid
    Exception: If index creation or data upload fails
"""

import sys
import os
from pinecone import ServerlessSpec

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from server.api.app import client  # pylint: disable=wrong-import-position
from utils.pc_index import pc  # pylint: disable=wrong-import-position

PC_INDEX = "ironhack-final-project"

if PC_INDEX not in pc.list_indexes().names():
    pc.create_index(
        name=PC_INDEX,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

index = pc.Index(PC_INDEX)

# Sample React code snippets
code_snippets = [
    {
        "id": "form-with-hooks",
        "text": """\
import React, { useState } from 'react';

function ContactForm() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log({ email, message });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="email" value={email} onChange={e => setEmail(e.target.value)} />
      <textarea value={message} onChange={e => setMessage(e.target.value)} />
      <button type="submit">Send</button>
    </form>
  );
}

export default ContactForm;
""",
        "tags": ["form", "hooks", "controlled-components"],
    },
    {
        "id": "fetch-api-effect",
        "text": """\
import React, { useEffect, useState } from 'react';

function UserList() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetch("https://jsonplaceholder.typicode.com/users")
      .then(res => res.json())
      .then(setUsers);
  }, []);

  return (
    <ul>
      {users.map(user => <li key={user.id}>{user.name}</li>)}
    </ul>
  );
}

export default UserList;
""",
        "tags": ["api", "fetch", "useEffect"],
    },
]

# Embed and upsert into Pinecone
for snippet in code_snippets:
    # Use the new OpenAI client syntax
    response = client.embeddings.create(
        input=snippet["text"], model="text-embedding-ada-002"
    )
    embedding = response.data[0].embedding

    index.upsert(
        [
            (
                snippet["id"],
                embedding,
                {"text": snippet["text"], "tags": ",".join(snippet["tags"])},
            )
        ]
    )

print("✅ Snippets uploaded to Pinecone.")
