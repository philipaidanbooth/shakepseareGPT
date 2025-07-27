"""
Script to parse Shakespeare HTML files and store scenes in a vector database.
"""

import os
import json
from bs4 import BeautifulSoup
import chromadb
from openai import OpenAI
import re
from dotenv import load_dotenv

load_dotenv()
# Initialize OpenAI
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Initialize ChromaDB Cloud
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")  
CHROMA_TENANT_ID = os.getenv("CHROMA_TENANT_ID")
CHROMA_DB_NAME = "Shakespeare_RAG_DB"

client = chromadb.CloudClient(
    api_key=CHROMA_API_KEY,
    tenant=CHROMA_TENANT_ID,
    database=CHROMA_DB_NAME
)

# Create or get collection
try:
    collection = client.get_collection(name="shakespeare_scenes")
    print("Using existing collection: shakespeare_scenes")
except:
    collection = client.create_collection(
        name="shakespeare_scenes",
        metadata={"desc": "Shakespeare scenes"}
    )
    print("Created new collection: shakespeare_scenes")

def roman_to_arabic(roman):
    """Convert Roman numerals to Arabic numbers."""
    roman_dict = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    result = 0
    prev = 0
    
    for char in roman.upper():
        curr = roman_dict.get(char, 0)
        if curr > prev:
            result += curr - 2 * prev
        else:
            result += curr
        prev = curr
    
    return result

def clean_text(text):
    """Clean and normalize text."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text) # replace multiple spaces with a single space
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text) # remove special characters but keep basic punctuation
    return text.strip()

def chunk_text(text, max_chars=15000):
    """Split text into chunks that fit within ChromaDB document size limits."""
    # ChromaDB free tier limit is 16,384 bytes, so we'll use 15,000 chars to be safe
    
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Split by sentences to avoid breaking mid-sentence
    sentences = text.split('. ')
    
    for sentence in sentences:
        if len(current_chunk + sentence) <= max_chars:
            current_chunk += sentence + '. '
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + '. '
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def extract_scenes_from_html(file_path, play_name):
    """Extract scenes from a Shakespeare HTML file."""
    with open(file_path, 'r', encoding='utf-8') as f: 
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    scenes = []
    
    # Find all scene headers (h3 tags with scene information)
    scene_headers = soup.find_all('h3')
    
    current_act = None
    current_scene = None
    current_scene_number = None
    current_scene_text = []
    current_characters = set()
    current_line_count = 0
    
    for element in soup.find_all(['h3', 'p', 'blockquote']):
        if element.name == 'h3':
            text = element.get_text().strip()
            
            # Check if this is an act header
            if text.upper().startswith('ACT'):
                current_act = text
                continue
            
            # Save previous scene if exists
            if current_scene and current_scene_text:
                scene_text = ' '.join(current_scene_text)
                if len(scene_text.strip()) > 50:  # Only save scenes with substantial content
                    scenes.append({
                        'title': current_scene,
                        'act': current_act,
                        'scene_number': current_scene_number,
                        'content': clean_text(scene_text),
                        'play': play_name,
                        'characters': list(current_characters),
                        'line_count': current_line_count,
                        'word_count': len(scene_text.split())
                    })
            
            # Start new scene - extract scene number from title
            current_scene = text
            current_scene_text = []
            current_characters = set()
            current_line_count = 0
            
            # Extract scene number from scene title (e.g., "SCENE I." -> 1, "SCENE II." -> 2)
            if text.upper().startswith('SCENE'):
                # Convert Roman numerals to Arabic numbers
                roman_numeral = text.split()[1].replace('.', '')
                current_scene_number = roman_to_arabic(roman_numeral)
            else:
                current_scene_number = None
        
        elif element.name in ['p', 'blockquote']:
            # Add text to current scene
            text = element.get_text().strip()
            if text:
                current_scene_text.append(text)
                current_line_count += 1
                
                # Extract character names from speech tags
                speech_tag = element.find_previous('a', {'name': lambda x: x and x.startswith('speech')})
                if speech_tag and speech_tag.find('b'):
                    character_name = speech_tag.find('b').get_text().strip()
                    current_characters.add(character_name)
    
    # Don't forget the last scene
    if current_scene and current_scene_text:
        scene_text = ' '.join(current_scene_text)
        if len(scene_text.strip()) > 50:
                            scenes.append({
                    'title': current_scene,
                    'act': current_act,
                    'scene_number': current_scene_number,
                    'content': clean_text(scene_text),
                    'play': play_name,
                    'characters': list(current_characters),
                    'line_count': current_line_count,
                    'word_count': len(scene_text.split())
                })
    
    return scenes

def main():
    """Main function to process all plays and store in vector database."""
    data_dir = "data"
    
    # Load plays metadata
    with open(os.path.join(data_dir, "plays_meta.json"), 'r') as f:
        plays_meta = json.load(f)
    
    all_scenes = []
    
    # Process each play
    for play_meta in plays_meta:
        play_name = play_meta['name']
        file_name = play_meta['file_name']
        html_file = os.path.join(data_dir, f"{file_name}.html")
        
        if os.path.exists(html_file):
            print(f"Processing {play_name}...")
            scenes = extract_scenes_from_html(html_file, play_name)
            all_scenes.extend(scenes)
            print(f"  Found {len(scenes)} scenes")
        else:
            print(f"Warning: {html_file} not found")
    
    print(f"\nTotal scenes found: {len(all_scenes)}")
    
    # Store scenes in vector database
    print("Storing scenes in vector database...")
    
    scene_id = 0
    successful_chunks = 0
    failed_chunks = 0
    
    for i, scene in enumerate(all_scenes):
        # Chunk the scene content if it's too long
        chunks = chunk_text(scene['content'])
        
        for chunk_idx, chunk in enumerate(chunks):
            try:
                # Create embedding using OpenAI
                response = openai_client.embeddings.create(
                    input=chunk,
                    model="text-embedding-3-small"
                )
                embedding = response.data[0].embedding
                
                # Add to collection
                collection.add(
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{
                        'play': scene['play'],
                        'act': scene['act'],
                        'scene_number': scene['scene_number'],
                        'scene_title': scene['title'],
                        'current_scene': f"{scene['act']} - {scene['title']}",
                        'scene_index': i,
                        'chunk_index': chunk_idx,
                        'total_chunks': len(chunks),
                        'characters': ', '.join(scene['characters']),
                        'line_count': scene['line_count'],
                        'word_count': scene['word_count']
                    }],
                    ids=[f"scene_{i}_chunk_{chunk_idx}"]
                )
                
                scene_id += 1
                successful_chunks += 1
                
            except Exception as e:
                print(f"Error processing scene {i}, chunk {chunk_idx}: {e}")
                print(f"Chunk length: {len(chunk)} characters")
                failed_chunks += 1
                continue
        
        if (i + 1) % 10 == 0: # print progress every 10 scenes
            print(f"  Processed {i + 1} scenes ({scene_id} total chunks)")
    
    print(f"Successfully stored {successful_chunks} chunks from {len(all_scenes)} scenes in vector database!")
    print(f"Failed to store {failed_chunks} chunks due to size limits.")
    
    # Test query
    print("\nTesting vector search...")
    results = collection.query(
        query_texts=["To be or not to be"],
        n_results=3
    )
    
    print("Top 3 results for 'To be or not to be':")
    for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
        print(f"{i+1}. {metadata['play']} - {metadata['scene_title']}")
        print(f"   Content: {doc[:200]}...")
        print()

if __name__ == "__main__":
    main() 