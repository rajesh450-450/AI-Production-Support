import time

from src.models.embeddings import embedding_model

for i in range(5):
    print(f"\nRun {i + 1}")

    vector = embedding_model.embed("Spark executor tuning")

    print(len(vector))

    time.sleep(2)