from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
mongodb_cluster = os.getenv("MONGODB_CLUSTER")
mongodb_username = os.getenv("MONGODB_USERNAME")
mongodb_pw = os.getenv("MONGODB_PW")

client = MongoClient(mongodb_cluster, 27017)
db = client["final_project_ai"]
messages_col = db["messages"]

base_api_url = "/api"
