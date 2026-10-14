# import os
# from dotenv import load_dotenv
# from google import genai

# load_dotenv()

# def embed(text: str):
#     client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

#     response = client.models.embed_content(
#         model="text-embedding-004",
#         contents=text,
#     )

#     return response.embeddings[0].values

# output = embed("hello")
# print(output)

from google import genai
import os

def embed(text):

    client = genai.Client(
        api_key=os.getenv("GOOGLE_API_KEY")
    )

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )

    return response.embeddings[0].values


print(len(embed("hello")))
print(len(embed("world")))
print(len(embed("python")))
print(len(embed("AI")))