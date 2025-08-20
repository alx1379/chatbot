import numpy as np
from typing import List

def similarity_calculator(question_embedding: List[float], content_embedding: List[float]) -> float:
    """
    Calculate cosine similarity between question and content embeddings.
    
    Args:
        question_embedding: Question vector
        content_embedding: Content vector
        
    Returns:
        Similarity score (float between -1 and 1, where 1 is most similar)
    """
    try:
        # Convert to numpy arrays
        q_vec = np.array(question_embedding)
        c_vec = np.array(content_embedding)
        
        # Handle zero vectors
        q_norm = np.linalg.norm(q_vec)
        c_norm = np.linalg.norm(c_vec)
        
        if q_norm == 0 or c_norm == 0:
            return 0.0
            
        # Calculate cosine similarity
        similarity = np.dot(q_vec, c_vec) / (q_norm * c_norm)
        
        return float(similarity)
        
    except Exception as e:
        print(f"Error calculating similarity: {str(e)}")
        return 0.0

if __name__ == "__main__":
    # Test similarity calculator
    # Create mock embeddings
    embedding1 = [0.1, 0.2, 0.3, 0.4] + [0.0] * 1532  # Pad to 1536
    embedding2 = [0.1, 0.2, 0.3, 0.4] + [0.0] * 1532  # Same as embedding1
    embedding3 = [-0.1, -0.2, -0.3, -0.4] + [0.0] * 1532  # Opposite
    
    sim1 = similarity_calculator(embedding1, embedding2)
    sim2 = similarity_calculator(embedding1, embedding3)
    
    print(f"Similarity (same): {sim1}")
    print(f"Similarity (opposite): {sim2}")
