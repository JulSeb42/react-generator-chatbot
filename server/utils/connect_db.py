"""Connect to MongoDB
All variables for MongoDB
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGODB_CLUSTER = os.getenv("MONGODB_CLUSTER")
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PW = os.getenv("MONGODB_PW")

client = MongoClient(MONGODB_CLUSTER, 27017)
db = client["final_project_ai"]
messages_col = db["messages"]
snippets_col = db["snippets"]

BASE_API_URL = "/api"
