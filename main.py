"""
ShakespeareGPT FastAPI Backend
Deployable on Railway
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv
import chromadb
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="ShakespeareGPT API",
    description="A RAG system for Shakespeare plays",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Pydantic models
class QuestionRequest(BaseModel):
    question: str
    k: Optional[int] = 3
    filters: Optional[Dict] = None

class SearchRequest(BaseModel):
    query: str
    k: Optional[int] = 5
    filters: Optional[Dict] = None

class SearchResult(BaseModel):
    content: str
    metadata: Dict
    distance: float

class AnswerResponse(BaseModel):
    answer: str
    sources: List[Dict]

# Helper functions
def search_shakespeare(query: str, k: int = 10, filters: Optional[Dict] = None):
    """Search Shakespeare scenes using semantic similarity."""
    try:
        # Validate inputs
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        if k <= 0 or k > 50:
            raise HTTPException(status_code=400, detail="k must be between 1 and 50")
        
        # Create embedding for the query
        print(f"🔍 Creating embedding for query: {query[:100]}...")
        response = openai_client.embeddings.create(
            input=query,
            model="text-embedding-3-small"
        )
        query_embedding = response.data[0].embedding
        
        # Build where clause for filters
        where_clause = None
        if filters:
            print(f"🔍 Applying filters: {filters}")
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
        print(f"🔍 Searching ChromaDB with k={k}...")
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
        
        print(f"✅ Found {len(formatted_results)} results")
        return formatted_results
    
    except Exception as e:
        print(f"❌ Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

def answer_with_shakespeare_context(question: str, k: int = 3, filters: Optional[Dict] = None):
    """Answer a question using Shakespeare context with optional filters.
    Models GPT-4o's style with specific quotes, context, and analysis."""
    try:
        # Validate inputs
        if not question or not question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        if k <= 0 or k > 20:
            raise HTTPException(status_code=400, detail="k must be between 1 and 20")
        
        # Step 1: Retrieve relevant Shakespeare chunks
        print(f"🔍 Searching Shakespeare database for: {question[:100]}...")
        if filters:
            print(f"🔍 Applying filters: {filters}")
        results = search_shakespeare(question, k=k, filters=filters)
        
        if not results:
            return "I couldn't find relevant Shakespeare content to answer your question.", []
        
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
        print("🤖 Generating answer with OpenAI...")
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
        print("✅ Answer generated successfully")
        
        # Step 5: Return answer with sources
        sources = []
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            similarity = 1 - result['distance']
            sources.append({
                "index": i,
                "play": metadata['play'],
                "act": metadata['act'],
                "scene_title": metadata['scene_title'],
                "similarity": round(similarity, 3)
            })
        
        return answer, sources
        
    except Exception as e:
        print(f"❌ Answer generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Answer generation error: {str(e)}")

# API endpoints
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "ShakespeareGPT API is running!",
        "version": "1.0.0",
        "endpoints": {
            "search": "/search",
            "answer": "/answer",
            "plays": "/plays",
            "characters": "/characters"
        }
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check for all services."""
    health_status = {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {}
    }
    
    # Test OpenAI connection
    try:
        test_response = openai_client.embeddings.create(
            input="test",
            model="text-embedding-3-small"
        )
        health_status["services"]["openai"] = "healthy"
    except Exception as e:
        health_status["services"]["openai"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Test ChromaDB connection
    try:
        test_results = collection.get(limit=1)
        health_status["services"]["chromadb"] = "healthy"
    except Exception as e:
        health_status["services"]["chromadb"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check environment variables
    env_vars = {}
    required_vars = ["OPENAI_API_KEY", "CHROMA_API_KEY", "CHROMA_TENANT_ID", "CHROMA_DB_NAME"]
    for var in required_vars:
        value = os.getenv(var)
        if value:
            env_vars[var] = "set"
        else:
            env_vars[var] = "missing"
            health_status["status"] = "unhealthy"
    
    health_status["environment"] = env_vars
    
    return health_status

@app.post("/search", response_model=List[SearchResult])
async def search_endpoint(request: SearchRequest):
    """Search Shakespeare scenes."""
    try:
        results = search_shakespeare(request.query, request.k, request.filters)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/answer", response_model=AnswerResponse)
async def answer_endpoint(request: QuestionRequest):
    """Answer questions using Shakespeare context."""
    try:
        answer, sources = answer_with_shakespeare_context(
            request.question, 
            request.k, 
            request.filters
        )
        return AnswerResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/plays")
async def get_plays():
    """Get list of all available plays."""
    try:
        results = collection.get(
            include=['metadatas'],
            limit=10000
        )
        
        plays = set()
        for metadata in results['metadatas']:
            if 'play' in metadata:
                plays.add(metadata['play'])
        
        return {"plays": sorted(list(plays))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/characters")
async def get_characters():
    """Get list of all available characters."""
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
        
        return {"characters": sorted(list(characters))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 