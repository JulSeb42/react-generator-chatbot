import os
from dotenv import load_dotenv


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

TOKEN_SECRET = os.getenv("TOKEN_SECRET")

CLIENT_URI = os.getenv("CLIENT_URI")

system_prompt = (
    "You are a senior React developer. Generate high-quality React code based on user requests.\n"
    "Use functional components, hooks, and modern best practices. If relevant, include helpful comments."
)
