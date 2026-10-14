from src.models.embeddings import embedding_model

embedding = embedding_model.embed(
    "I work at Mastercard."
)

print(f"Embedding Dimension : {len(embedding)}")

print()
print(embedding[:10])