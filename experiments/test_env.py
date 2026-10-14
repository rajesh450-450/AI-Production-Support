import os
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv()

print("Loaded .env:", dotenv_path)

load_dotenv(dotenv_path)

print("API KEY configured:", bool(os.getenv("GOOGLE_API_KEY")))
print("MODEL:", os.getenv("MODEL_NAME"))