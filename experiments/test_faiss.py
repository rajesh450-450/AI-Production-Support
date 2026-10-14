import faiss
import numpy as np

print("FAISS Version:", faiss.__version__)

dimension = 4

index = faiss.IndexFlatL2(dimension)

print("Index created successfully.")

vector = np.array(
    [[1.0, 2.0, 3.0, 4.0]],
    dtype="float32"
)

index.add(vector)

print("Vectors in index:", index.ntotal)