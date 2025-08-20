from openai import OpenAI
import os
from typing import List
import numpy as np

def content_embedder(text: str) -> List[float]:
    """
    Generate embeddings for text content using OpenAI's embedding model.
    
    Args:
        text: Text to embed
        
    Returns:
        Vector of 1536 floats (OpenAI embedding)
    """
    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
        
        # Truncate text if too long (OpenAI has token limits)
        if len(text) > 8000:  # Rough character limit
            text = text[:8000] + "..."
            
        response = client.embeddings.create(
            model="text-embedding-3-small",  # 1536 dimensions
            input=text
        )
        
        return response.data[0].embedding
        
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        # Return zero vector as fallback
        return [0.0] * 1536

if __name__ == "__main__":
    # Test the embedder
    test_text = "This is a test document about return policies and customer service."
    embedding = content_embedder(test_text)
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
