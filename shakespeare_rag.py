"""
Shakespeare RAG System
Uses retrieved Shakespeare chunks to generate contextual answers.
"""

import chromadb
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize ChromaDB Cloud client
client = chromadb.CloudClient(
    api_key=os.getenv("CHROMA_API_KEY"),
    tenant=os.getenv("CHROMA_TENANT_ID"),
    database=os.getenv("CHROMA_DB_NAME")
)

# Get the collection
collection = client.get_collection(name="shakespeare_scenes")

# ------------------------------------------------------------

def search_shakespeare(query, k=10, filters=None):
    """
    Search Shakespeare scenes using semantic similarity with optional filters.
    
    Args:
        query (str): The search query
        k (int): Number of results to return
        filters (dict): Optional filters like {"play": "Hamlet", "act": "ACT I"}
    """
    try:
        # Create embedding for the query
        response = openai_client.embeddings.create(
            input=query,
            model="text-embedding-3-small"
        )
        query_embedding = response.data[0].embedding
        
        # Build where clause for filters
        where_clause = None
        if filters:
            where_conditions = []
            for key, value in filters.items():
                if key in ['play', 'act', 'scene_number', 'characters']:
                    where_conditions.append({key: {"$eq": value}})
            
            # Handle single vs multiple conditions
            if len(where_conditions) == 1:
                where_clause = where_conditions[0]
            elif len(where_conditions) > 1:
                where_clause = {"$and": where_conditions}
        
        # Search the collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=where_clause,
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

def list_available_plays():
    """Get list of all available plays in the database."""
    try:
        # Get unique plays from the collection
        results = collection.get(
            include=['metadatas'],
            limit=10000  # Get all documents
        )
        
        plays = set()
        for metadata in results['metadatas']:
            if 'play' in metadata:
                plays.add(metadata['play'])
        
        return sorted(list(plays))
    except Exception as e:
        print(f"Error getting plays: {e}")
        return []

def list_available_characters():
    """Get list of all available characters in the database."""
    try:
        results = collection.get(
            include=['metadatas'],
            limit=10000
        )
        
        characters = set()
        for metadata in results['metadatas']:
            if 'characters' in metadata:
                char_list = metadata['characters'].split(', ')
                characters.update(char_list)
        
        return sorted(list(characters))
    except Exception as e:
        print(f"Error getting characters: {e}")
        return []

# ------------------------------------------------------------

def answer_with_shakespeare_context(question, k=3, filters=None):
    """
    Answer a question using Shakespeare context with optional filters.
    Models GPT-4o's style with specific quotes, context, and analysis.
    
    Args:
        question (str): The question to answer
        k (int): Number of relevant chunks to retrieve
        filters (dict): Optional filters like {"play": "Hamlet"}
    
    Returns:
        str: Generated answer with Shakespeare context in GPT-4o style
    """
    # Step 1: Retrieve relevant Shakespeare chunks
    print("🔍 Searching Shakespeare database...")
    if filters:
        print(f"🔍 Applying filters: {filters}")
    results = search_shakespeare(question, k=k, filters=filters)
    
    if not results:
        return "I couldn't find relevant Shakespeare content to answer your question."
    
    # Step 2: Build context from retrieved chunks
    context_parts = []
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        content = result['content']
        similarity = 1 - result['distance']
        
        context_parts.append(f"""
--- Source {i} ---
Play: {metadata['play']}
Act: {metadata['act']}
Scene: {metadata['scene_title']}
Characters: {metadata['characters']}
Relevance: {similarity:.3f}
Content: {content}
""")
    
    context = "\n".join(context_parts)
    
    # Step 3: Create prompt that models GPT-4o's style
    prompt = f"""You are a Shakespeare scholar providing detailed, analytical responses in the style of GPT-4o. When answering questions about Shakespeare's works, follow this approach:

1. **Provide Context**: Set the scene and explain the dramatic situation
2. **Quote Specifically**: Include exact quotes from the text with proper attribution
3. **Analyze the Moment**: Explain the significance and what it reveals about characters/themes
4. **Connect to Broader Themes**: Show how this moment fits into the larger play
5. **Use Clear Structure**: Organize your response with clear paragraphs and transitions

Use markdown formatting for better readability:
- Use **bold** for emphasis and section headers
- Use *italic* for character names and play titles
- Structure your response with clear sections
- Format quotes with proper attribution

CONTEXT FROM SHAKESPEARE'S WORKS:
{context}

QUESTION: {question}

Please provide a thoughtful, well-structured response that:
- Identifies the specific moment/scene being asked about
- Includes relevant quotes with proper attribution (Act, Scene)
- Explains the dramatic context and significance
- Analyzes what this reveals about the character(s) and themes
- Uses a scholarly but accessible tone similar to GPT-4o
- Uses markdown formatting for better structure

RESPONSE:"""

    # Step 4: Generate answer using OpenAI
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a Shakespeare scholar providing detailed, analytical responses. When quoting Shakespeare, always include the Act and Scene. Structure your responses with clear context, specific quotes, and thoughtful analysis. Aim for the depth and clarity of GPT-4o's responses."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        
        # Step 5: Add source information
        sources_info = "\n\n📚 Sources:\n"
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            similarity = 1 - result['distance']
            sources_info += f"{i}. {metadata['play']} - {metadata['act']} - {metadata['scene_title']} (Relevance: {similarity:.3f})\n"
        
        return answer + sources_info
        
    except Exception as e:
        return f"Error generating answer: {e}"

def interactive_shakespeare_qa():
    """Interactive Q&A session with Shakespeare context in GPT-4o style."""
    print("🎭 Shakespeare RAG System (GPT-4o Style)")
    print("Ask questions about Shakespeare and get detailed, analytical responses with specific quotes!")
    print("Type 'quit' to exit.\n")
    
    while True:
        question = input("❓ Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not question:
            continue
        
        print("\n🤔 Analyzing Shakespeare's works...")
        answer = answer_with_shakespeare_context(question)
        print(f"\n💡 Answer:\n{answer}")
        print("\n" + "="*80 + "\n")

# Example usage
if __name__ == "__main__":
    # Test the RAG system
    test_questions = [
        "What does Hamlet say about death?",
        "How does Romeo describe Juliet?",
        "What is Macbeth's reaction to the witches' prophecy?"
    ]
    
    print("🎭 Testing Shakespeare RAG System")
    print("="*50)
    
    for question in test_questions:
        print(f"\n🎭 Question: {question}")
        answer = answer_with_shakespeare_context(question)
        print(f"💡 Answer:\n{answer}")
        print("-" * 80)
    
    # Uncomment to run interactive mode
    # interactive_shakespeare_qa() 