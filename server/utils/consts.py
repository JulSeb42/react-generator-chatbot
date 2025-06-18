import os
from dotenv import load_dotenv, find_dotenv

base_api_url = "/api"

_ = load_dotenv(find_dotenv())

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
