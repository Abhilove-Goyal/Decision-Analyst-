from sentence_transformers import CrossEncoder
from functools import lru_cache
from typing import List

# Load once (important for performance)
@lru_cache(maxsize=1)
def _get_cross_encoder():
    return CrossEncoder("BAAI/bge-reranker-large")

def rerank(query: str, chunks: List[dict], top_k: int = 5) -> List[dict]:
    """
    Rerank chunks using BAAI/bge-reranker-large.
    """
    if not chunks:
        return []
    
    encoder = _get_cross_encoder()
    
    # Prepare pairs: (query, chunk_text)
    pairs = [(query, chunk['chunk_text']) for chunk in chunks]
    
    # Predict scores
    scores = encoder.predict(pairs)
    
    # Sort chunks by scores descending
    scored_chunks = list(zip(chunks, scores))
    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    
    # Return top_k
    return [chunk for chunk, score in scored_chunks[:top_k]]
