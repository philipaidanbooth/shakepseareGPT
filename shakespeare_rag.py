"""
Shakespeare RAG System
Uses retrieved Shakespeare chunks to generate contextual answers.
"""

import chromadb
import os
from dotenv import load_dotenv
from openai import OpenAI
from langchain.chains.query_constructor.base import AttributeInfo

from notebook_setup import query


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

metadata_field_info = [
    AttributeInfo(name="play", description="The title of the Shakespeare play", type="string"),
    AttributeInfo(name="act", description="The act of the play, like 'ACT I'", type="string"),
    AttributeInfo(name="scene_number", description="Scene number within the act", type="string"),
    AttributeInfo(name="scene_index", description="Index of the scene (zero-based)", type="string"),
    AttributeInfo(name="characters", description="Characters present in the scene", type="string"),
]

examples = [
    (
        "When does Bertram first speak in All's Well That Ends Well?",
        {
            "query": "Bertram's first lines",
            "filter": 'and(eq("play", "All\'s Well That Ends Well"), eq("characters", "BERTRAM"))'
        }
    ),
    (
        "Scene 1 of Act I in All's Well That Ends Well",
        {
            "query": "Scene details",
            "filter": 'and(eq("play", "All\'s Well That Ends Well"), eq("act", "ACT I"), eq("scene_number", "1"))'
        }
    )
]






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
            if where_conditions:
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

def search_by_play(play_name, query="", k=5):
    """Search within a specific play."""
    filters = {"play": play_name}
    return search_shakespeare(query, k=k, filters=filters)

def search_by_act(play_name, act_name, query="", k=5):
    """Search within a specific act of a play."""
    filters = {"play": play_name, "act": act_name}
    return search_shakespeare(query, k=k, filters=filters)

def search_by_character(character_name, query="", k=5):
    """Search scenes containing a specific character."""
    filters = {"characters": character_name}
    return search_shakespeare(query, k=k, filters=filters)

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
    
    Args:
        question (str): The question to answer
        k (int): Number of relevant chunks to retrieve
        filters (dict): Optional filters like {"play": "Hamlet"}
    
    Returns:
        str: Generated answer with Shakespeare context
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
        context_parts.append(f"""
--- Source {i} ---
Play: {metadata['play']}
Act: {metadata['act']}
Scene: {metadata['scene_title']}
Characters: {metadata['characters']}
Content: {result['content']}
""")
    
    context = "\n".join(context_parts)
    
    # Step 3: Create prompt with context
    prompt = f"""You are a well-read, insightful Shakespeare guide—a scholar and storyteller who can explain the Bard's works to students, readers, and performers alike.

            Below is a passage or excerpt from Shakespeare. Use it to thoughtfully respond to the user's question.

            CONTEXT:
            {context}

            QUESTION:
            {query}

            Please provide a thoughtful, well-supported response based on the context above. Feel free to cite specific characters, scenes, or quotes when relevant. If the passage doesn’t fully answer the question, acknowledge that and share whatever insight you can based on the given lines. Aim for clarity, depth, and a touch of literary flair where appropriate.

            RESPONSE:"""

    # Step 4: Generate answer using OpenAI
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a thoughtful, insightful guide to Shakespeare’s works—combining deep literary knowledge with clear, approachable explanations. You help students, scholars, and theater-lovers understand scenes, characters, and themes based on the provided context. If the passage is unclear or insufficient, you explain what can and can’t be answered."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        
        # Step 5: Return answer with sources
        sources_info = "\n\n📚Top 3 Chunks:\n"
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            similarity = 1 - result['distance']
            sources_info += f"{i}. {metadata['play']} - {metadata['act']} - {metadata['scene_title']} (Similarity: {similarity:.3f})\n"
        
        return answer + sources_info
        
    except Exception as e:
        return f"Error generating answer: {e}"







# ------------------------------------------------------------

def interactive_shakespeare_qa():
    """Interactive Q&A session with Shakespeare context."""
    print("🎭 Shakespeare RAG System")
    print("Ask questions about Shakespeare and get contextual answers!")
    print("Type 'quit' to exit.\n")
    
    while True:
        question = input("❓ Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not question:
            continue
        
        print("\n🤔 Thinking...")
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
    
    for question in test_questions:
        print(f"\n🎭 Question: {question}")
        answer = answer_with_shakespeare_context(question)
        print(f"💡 Answer:\n{answer}")
        print("-" * 80)
    
    # ------------------------------------------------------------
    
    
    # Uncomment to run interactive mode
    interactive_shakespeare_qa() 