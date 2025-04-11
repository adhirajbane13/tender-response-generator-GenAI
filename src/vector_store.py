import os
from dotenv import load_dotenv
from typing import List
import faiss
import openai
from sklearn.preprocessing import normalize
import numpy as np
from openai import OpenAI
from difflib import SequenceMatcher

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed_texts(chunks: List[tuple]) -> np.ndarray:
    """
    Getting OpenAI embeddings for a list of (title, text) chunks and return as numpy array
    """
    texts = [text for _, text in chunks]  # Extracting only the text part from the tuples
    response = client.embeddings.create(
        input=texts,  # list of strings
        model="text-embedding-3-large"
    )
    embeddings = [item.embedding for item in response.data]
    
    # Normalizing vectors
    embeddings = np.array(embeddings)
    return normalize(embeddings)

def build_faiss_index(chunks: List[str]):
    """
    Embedding the text chunks and build a FAISS index
    """
    vectors = embed_texts(chunks)

    dimension = vectors.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)

    return index, vectors

def search_faiss_index(query: str, index, chunks: List[str], k: int = 10) -> List[str]:
    """
    Searching the FAISS index with a user query and return top-k relevant chunks
    """
    # Embedding the query
    response = client.embeddings.create(
        input=[query],
        model="text-embedding-3-large"
    )
    query_vector = np.array(response.data[0].embedding).reshape(1, -1)

    # Step 2: Search FAISS
    distances, indices = index.search(query_vector, k)

    # Step 3: Retrieve matching chunks
    results = [chunks[i] for i in indices[0]]
    return results

