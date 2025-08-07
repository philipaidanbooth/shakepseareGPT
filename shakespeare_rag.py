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

def extract_quotes_from_text(text, min_length=10):
    """
    Extract potential quotes from text by looking for dialogue patterns.
    
    Args:
        text (str): The text to extract quotes from
        min_length (int): Minimum length for a quote to be considered
    
    Returns:
        list: List of potential quotes
    """
    quotes = []
    
    # Split by lines and look for dialogue patterns
    lines = text.split('\n')
    current_quote = ""
    
    for line in lines:
        line = line.strip()
        
        # Look for character names followed by dialogue (common Shakespeare format)
        if ':' in line and len(line.split(':')[0].strip()) < 20:  # Character name likely
            parts = line.split(':', 1)
            if len(parts) == 2:
                dialogue = parts[1].strip()
                if len(dialogue) >= min_length:
                    quotes.append(dialogue)
        
        # Look for lines that start with capital letters and seem like dialogue
        elif line and line[0].isupper() and len(line) >= min_length:
            # Check if it looks like dialogue (not stage directions)
            if not any(word in line.upper() for word in ['ENTER', 'EXIT', 'SCENE', 'ACT', 'STAGE']):
                quotes.append(line)
    
    return quotes

def get_quotes_from_chunks(question, k=5, filters=None, max_quotes_per_chunk=3):
    """
    Get specific quotes from relevant Shakespeare chunks.
    
    Args:
        question (str): The search query
        k (int): Number of relevant chunks to retrieve
        filters (dict): Optional filters like {"play": "Hamlet"}
        max_quotes_per_chunk (int): Maximum quotes to extract per chunk
    
    Returns:
        dict: Dictionary with quotes organized by source
    """
    # Step 1: Retrieve relevant Shakespeare chunks
    print("🔍 Searching Shakespeare database for quotes...")
    if filters:
        print(f"🔍 Applying filters: {filters}")
    results = search_shakespeare(question, k=k, filters=filters)
    
    if not results:
        return {"error": "I couldn't find relevant Shakespeare content."}
    
    # Step 2: Extract quotes from each chunk
    quotes_by_source = {}
    
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        content = result['content']
        similarity = 1 - result['distance']
        
        # Extract quotes from this chunk
        quotes = extract_quotes_from_text(content)
        
        # Limit quotes per chunk
        quotes = quotes[:max_quotes_per_chunk]
        
        source_info = {
            'play': metadata['play'],
            'act': metadata['act'],
            'scene_title': metadata['scene_title'],
            'characters': metadata['characters'],
            'similarity': similarity,
            'quotes': quotes
        }
        
        quotes_by_source[f"Source {i}"] = source_info
    
    return quotes_by_source

def format_quotes_response(quotes_by_source):
    """
    Format the quotes response for display.
    
    Args:
        quotes_by_source (dict): Quotes organized by source
    
    Returns:
        str: Formatted response with quotes
    """
    if "error" in quotes_by_source:
        return quotes_by_source["error"]
    
    response = "📚 Relevant Shakespeare Quotes:\n\n"
    
    for source_name, source_info in quotes_by_source.items():
        response += f"🎭 {source_name}\n"
        response += f"📖 Play: {source_info['play']}\n"
        response += f"🎪 Act: {source_info['act']}\n"
        response += f"🎬 Scene: {source_info['scene_title']}\n"
        response += f"👥 Characters: {source_info['characters']}\n"
        response += f"📊 Relevance: {source_info['similarity']:.3f}\n\n"
        
        if source_info['quotes']:
            response += "💬 Quotes:\n"
            for j, quote in enumerate(source_info['quotes'], 1):
                response += f"   {j}. \"{quote}\"\n"
        else:
            response += "💬 No specific quotes found in this chunk.\n"
        
        response += "\n" + "-" * 60 + "\n\n"
    
    return response

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
    
    # Step 2: Extract quotes from chunks for more precise responses
    quotes_by_source = {}
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        content = result['content']
        similarity = 1 - result['distance']
        
        # Extract quotes from this chunk
        quotes = extract_quotes_from_text(content)
        
        source_info = {
            'play': metadata['play'],
            'act': metadata['act'],
            'scene_title': metadata['scene_title'],
            'characters': metadata['characters'],
            'similarity': similarity,
            'quotes': quotes,
            'full_content': content
        }
        
        quotes_by_source[f"Source {i}"] = source_info
    
    # Step 3: Build context with specific quotes
    context_parts = []
    for source_name, source_info in quotes_by_source.items():
        context_parts.append(f"""
--- {source_name} ---
Play: {source_info['play']}
Act: {source_info['act']}
Scene: {source_info['scene_title']}
Characters: {source_info['characters']}
Relevance: {source_info['similarity']:.3f}
Key Quotes: {chr(10).join([f'"{quote}"' for quote in source_info['quotes'][:3]])}
Full Content: {source_info['full_content']}
""")
    
    context = "\n".join(context_parts)
    
    # Step 4: Create prompt that models GPT-4o's style
    prompt = f"""You are a Shakespeare scholar providing detailed, analytical responses in the style of GPT-4o. When answering questions about Shakespeare's works, follow this approach:

1. **Provide Context**: Set the scene and explain the dramatic situation
2. **Quote Specifically**: Include exact quotes from the text with proper attribution
3. **Analyze the Moment**: Explain the significance and what it reveals about characters/themes
4. **Connect to Broader Themes**: Show how this moment fits into the larger play
5. **Use Clear Structure**: Organize your response with clear paragraphs and transitions

CONTEXT FROM SHAKESPEARE'S WORKS:
{context}

QUESTION: {question}

Please provide a thoughtful, well-structured response that:
- Identifies the specific moment/scene being asked about
- Includes relevant quotes with proper attribution (Act, Scene)
- Explains the dramatic context and significance
- Analyzes what this reveals about the character(s) and themes
- Uses a scholarly but accessible tone similar to GPT-4o

RESPONSE:"""

    # Step 5: Generate answer using OpenAI
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
        
        # Step 6: Add source information
        sources_info = "\n\n📚 Sources:\n"
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            similarity = 1 - result['distance']
            sources_info += f"{i}. {metadata['play']} - {metadata['act']} - {metadata['scene_title']} (Relevance: {similarity:.3f})\n"
        
        return answer + sources_info
        
    except Exception as e:
        return f"Error generating answer: {e}"







# ------------------------------------------------------------

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

def interactive_quotes_mode():
    """Interactive mode specifically for getting quotes from Shakespeare chunks."""
    print("📚 Shakespeare Quotes Mode")
    print("Get specific quotes from Shakespeare's works!")
    print("Commands:")
    print("  - Type your question to get relevant quotes")
    print("  - Type 'filter:play=Hamlet' to filter by play")
    print("  - Type 'filter:character=HAMLET' to filter by character")
    print("  - Type 'quit' to exit\n")
    
    current_filters = None
    
    while True:
        user_input = input("🔍 Search for quotes: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Check for filter commands
        if user_input.startswith('filter:'):
            filter_parts = user_input[7:].split('=')
            if len(filter_parts) == 2:
                filter_type = filter_parts[0].strip()
                filter_value = filter_parts[1].strip()
                
                if current_filters is None:
                    current_filters = {}
                
                if filter_type == 'play':
                    current_filters['play'] = filter_value
                    print(f"✅ Filter set: Play = {filter_value}")
                elif filter_type == 'character':
                    current_filters['characters'] = filter_value
                    print(f"✅ Filter set: Character = {filter_value}")
                else:
                    print("❌ Invalid filter type. Use 'play' or 'character'")
            continue
        
        # Clear filters
        if user_input.lower() == 'clear filters':
            current_filters = None
            print("✅ Filters cleared")
            continue
        
        # Show current filters
        if user_input.lower() == 'show filters':
            if current_filters:
                print("🔍 Current filters:")
                for key, value in current_filters.items():
                    print(f"  {key}: {value}")
            else:
                print("🔍 No filters applied")
            continue
        
        # Get quotes
        print("\n🔍 Searching for quotes...")
        quotes_result = get_quotes_from_chunks(user_input, k=5, filters=current_filters)
        formatted_response = format_quotes_response(quotes_result)
        print(f"\n{formatted_response}")
        print("="*80 + "\n")

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
    
    # Test regular RAG
    print("\n📝 Testing Regular RAG Mode:")
    for question in test_questions:
        print(f"\n🎭 Question: {question}")
        answer = answer_with_shakespeare_context(question)
        print(f"💡 Answer:\n{answer}")
        print("-" * 80)
    
    # Test quotes mode
    print("\n📚 Testing Quotes Mode:")
    test_quote_questions = [
        "Hamlet's famous soliloquy",
        "Romeo's love for Juliet",
        "Macbeth's ambition"
    ]
    
    for question in test_quote_questions:
        print(f"\n🔍 Question: {question}")
        quotes_result = get_quotes_from_chunks(question, k=3)
        formatted_response = format_quotes_response(quotes_result)
        print(f"{formatted_response}")
        print("-" * 80)
    
    # ------------------------------------------------------------
    
    # Uncomment to run interactive mode
    # interactive_shakespeare_qa()
    
    # Uncomment to run quotes mode
    # interactive_quotes_mode() 