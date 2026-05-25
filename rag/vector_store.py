import os

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from rag.chunking import create_chunks


def create_vector_store(file_path, mttr_path=None):

    print("\nCreating chunks...\n")

    # Pass both paths to chunking
    chunks = create_chunks(file_path, mttr_path)

    print("\nLoading embedding model...\n")

    # Free local embedding model
    model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

    print("\nCreating embeddings...\n")

    embeddings = model.encode(chunks)

    # Convert to numpy array
    embeddings = np.array(embeddings)

    print(f"\nEmbeddings Shape: {embeddings.shape}")

    # Create FAISS index
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    print("\nVector database created successfully.\n")

    return index, chunks, model


if __name__ == "__main__":

    create_vector_store(
        "downloads/tappetbox_report.csv",
        "downloads/mttr_mtbf_report.xlsx"
    )