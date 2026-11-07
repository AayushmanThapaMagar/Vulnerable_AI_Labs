import json
import os
from pathlib import Path

import numpy as np 
from dotenv import load_dotenv 
from google import genai
from google.genai import types 

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def normalize_rows(matrix): 
    """Scale each vector to length 1 without changing its direction."""
    if not np.isfinite(matrix).all():
        raise ValueError("Vectors contain invalid numbers.")
    
    lengths = np.linalg.norm(matrix, axis=1, keepdims=True)
    
    if np.any(lengths == 0): 
        raise ValueError("Cannot normalize a zero-length vector.")
    
    return matrix / lengths

def retrieve(question, top_k = 3):
    if not question.strip():
        raise ValueError("The question must not be empty.")
    
    if top_k < 1: 
        raise ValueError("top_k must be positive.")
    
    load_dotenv(PROJECT_ROOT.parent / ".env")
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key: 
        raise ValueError("Set GEMINI_API_KEY in .env.")
    
    index_path = PROJECT_ROOT / "data" / "processed" / "embeddings.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    
    chunks = index["chunks"]
    dimensions = index["dimensions"]
    
    if not chunks: 
        raise ValueError("The saved index contains no chunks.")
    
    if index["task_type"] != "RETRIEVAL_DOCUMENT": 
        raise ValueError("Expected document retrieval embeddings.")
    
    document_vectors = np.array(
        [chunk["embedding"] for chunk in chunks],
        dtype = np.float64, 
    )
    
    document_vectors = normalize_rows(document_vectors)
    
    with genai.Client(api_key=api_key) as client: 
        response = client.models.embed_content(
            model = index["model"],
            contents = question,
            config = types.EmbedContentConfig(
                task_type = "RETRIEVAL_QUERY",
                output_dimensionality = dimensions, 
            ),
        )
    
    embeddings = response.embeddings or []
    
    if len(embeddings) != 1 or embeddings[0].values is None: 
        raise ValueError("Expected one question embedding.")
    
    question_vector = np.array(
        [embeddings[0].values],
        dtype = np.float64,
    )
    
    if question_vector.shape != (1, dimensions): 
        raise ValueError("Unexpected question vector dimensions.")
    
    question_vector = normalize_rows(question_vector)[0]
    
    # Dot products of  unit vectors equal cosine similarities. 
    scores = document_vectors @ question_vector
    
    ranked_indices = np.argsort(-scores, kind="stable")[:top_k]
    
    return [
        {
            "chunk_id": chunks[i]["chunk_id"],
            "source": chunks[i]["source"], 
            "text": chunks[i]["text"], 
            "score": float(scores[i]),
        }
        for i in ranked_indices
    ]
    

def main(): 
    question = input("Search question: ").strip()
    results = retrieve(question)
    
    for rank, result in enumerate(results, start = 1):
        print(
            f"\n{rank}. {result['chunk_id']}"
            f"| score = {result['score']:.4f}"
        )
        print(f"Source: {result['source']}")
        print(result["text"])
        
        
if __name__ == "__main__":
    main()