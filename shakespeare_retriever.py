"""
Shakespeare ChromaDB Retriever
Loads the Shakespeare vector database and provides search functionality.
"""

import chromadb
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client for embeddings
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize ChromaDB Cloud client
client = chromadb.CloudClient(
    api_key=os.getenv("CHROMA_API_KEY"),
    tenant=os.getenv("CHROMA_TENANT_ID"),
    database=os.getenv("CHROMA_DB_NAME")
)

# Get the collection
collection = client.get_collection(name="shakespeare_scenes")

def search_shakespeare(query, k=5):
    """
    Search Shakespeare scenes using semantic similarity.
    
    Args:
        query (str): The search query
        k (int): Number of results to return
    
    Returns:
        list: List of dictionaries with search results
    """
    try:
        # Create embedding for the query
        response = openai_client.embeddings.create(
            input=query,
            model="text-embedding-3-small"
        )
        query_embedding = response.data[0].embedding
        
        # Search the collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })
        
        return formatted_results
    
    except Exception as e:
        print(f"Error searching: {e}")
        return []

def print_search_results(results):
    """Pretty print search results."""
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Play: {result['metadata']['play']}")
        print(f"Act: {result['metadata']['act']}")
        print(f"Scene: {result['metadata']['scene_title']}")
        print(f"Characters: {result['metadata']['characters']}")
        print(f"Similarity Score: {1 - result['distance']:.3f}")
        print(f"Content Preview: {result['content'][:200]}...")
        print("-" * 50)

# Example usage
if __name__ == "__main__":
    # Test the retriever
    print("🔍 Shakespeare Retriever Loaded!")
    print("Testing with 'To be or not to be'...")
    
    results = search_shakespeare("To be or not to be", k=3)
    print_search_results(results)
    
    print("\n" + "="*60)
    print("🎭 Shakespeare Database Ready!")
    print("Use search_shakespeare('your query', k=5) to search")
    print("Use print_search_results(results) to display results")
    print("="*60) 