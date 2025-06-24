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
snippets_col = db["snippets"]

base_api_url = "/api"

# import sqlite3
# import os
# from contextlib import contextmanager

# # Database file path
# DB_PATH = os.path.join(os.path.dirname(__file__), "..", "final_project_ai.db")


# def init_db():
#     """Initialize the SQLite database with required tables"""
#     with sqlite3.connect(DB_PATH) as conn:
#         conn.execute(
#             """
#             CREATE TABLE IF NOT EXISTS messages (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 message TEXT,
#                 role TEXT,
#                 session_id TEXT,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )
#         """
#         )

#         conn.execute(
#             """
#             CREATE TABLE IF NOT EXISTS snippets (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 text TEXT,
#                 tags TEXT,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )
#         """
#         )

#         conn.commit()


# @contextmanager
# def get_db_connection():
#     """Context manager for database connections"""
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row  # This allows dict-like access to rows
#     try:
#         yield conn
#     finally:
#         conn.close()


# # Initialize the database when this module is imported
# init_db()


# def fetch_all():
#     with get_db_connection() as conn:
#         cursor = conn.execute("SELECT * FROM messages ORDER BY created_at")
#         return [dict(row) for row in cursor.fetchall()]


# base_api_url = "/api"
