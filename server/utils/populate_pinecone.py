import openai
from pinecone import ServerlessSpec
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import pc

pc_index = "ironhack-final-project"

if pc_index not in pc.list_indexes().names():
    pc.create_index(
        name=pc_index,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

index = pc.Index(pc_index)

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
    response = openai.Embedding.create(
        input=snippet["text"], model="text-embedding-ada-002"
    )
    embedding = response["data"][0]["embedding"]
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
