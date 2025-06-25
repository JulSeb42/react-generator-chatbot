# from pinecone import Pinecone, ServerlessSpec
# from utils.consts import PINECONE_API_KEY

# pc = Pinecone(api_key=PINECONE_API_KEY)
# pc_index = "ironhack-final-project"

# if pc_index not in pc.list_indexes().names():
#     pc.create_index(
#         name=pc_index,
#         dimension=1536,
#         metric="cosine",
#         spec=ServerlessSpec(cloud="aws", region="us-east-1"),
#     )

# index = pc.Index(pc_index)

from pinecone import Pinecone
import os
from utils.consts import PINECONE_API_KEY

# Initialize Pinecone with new v5+ syntax
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("ironhack-final-project")