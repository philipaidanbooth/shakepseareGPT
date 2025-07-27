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
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

def answer_with_shakespeare_context(question: str, k: int = 3, filters: Optional[Dict] = None):
    """Answer a question using Shakespeare context."""
    try:
        # Retrieve relevant Shakespeare chunks
        results = search_shakespeare(question, k=k, filters=filters)
        
        if not results:
            return "I couldn't find relevant Shakespeare content to answer your question.", []
        
        # Build context from retrieved chunks
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
        
        # Create prompt with context
        prompt = f"""You are a well-read, insightful Shakespeare guide—a scholar and storyteller who can explain the Bard's works to students, readers, and performers alike.

Below is a passage or excerpt from Shakespeare. Use it to thoughtfully respond to the user's question.

CONTEXT:
{context}

QUESTION:
{question}

Please provide a thoughtful, well-supported response based on the context above. Feel free to cite specific characters, scenes, or quotes when relevant. If the passage doesn't fully answer the question, acknowledge that and share whatever insight you can based on the given lines. Aim for clarity, depth, and a touch of literary flair where appropriate.

RESPONSE:"""

        # Generate answer using OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a thoughtful, insightful guide to Shakespeare's works—combining deep literary knowledge with clear, approachable explanations. You help students, scholars, and theater-lovers understand scenes, characters, and themes based on the provided context. If the passage is unclear or insufficient, you explain what can and can't be answered."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        
        # Format sources
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