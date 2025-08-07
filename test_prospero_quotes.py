#!/usr/bin/env python3
"""
Test script specifically for Prospero quotes
"""

from shakespeare_rag import get_quotes_from_chunks, format_quotes_response, search_shakespeare, list_available_plays

def find_tempest_play_name():
    """Find the exact Tempest play name in the database."""
    plays = list_available_plays()
    for play in plays:
        if "tempest" in play.lower():
            return play
    return None

def test_prospero_quotes():
    """Test finding Prospero's famous quotes."""
    
    print("🎭 Testing Prospero Quote Extraction")
    print("="*50)
    
    # Find the correct Tempest play name
    tempest_play = find_tempest_play_name()
    if not tempest_play:
        print("❌ The Tempest not found in database!")
        return
    
    print(f"✅ Using play name: {tempest_play}")
    
    # Test different queries for Prospero
    queries = [
        "Prospero rough magic abjure",
        "Prospero leave island tempest",
        "Prospero break staff bury book",
        "Prospero Act V Scene I",
        "Prospero magic renunciation"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 40)
        
        # Get quotes without filters
        quotes_result = get_quotes_from_chunks(query, k=5)
        formatted_response = format_quotes_response(quotes_result)
        print(formatted_response)
        
        print("="*80)

def test_tempest_specific():
    """Test with Tempest-specific filters."""
    
    print("\n🎭 Testing Tempest-Specific Search")
    print("="*50)
    
    # Find the correct Tempest play name
    tempest_play = find_tempest_play_name()
    if not tempest_play:
        print("❌ The Tempest not found in database!")
        return
    
    print(f"✅ Using play name: {tempest_play}")
    
    # Test with Tempest filter
    quotes_result = get_quotes_from_chunks("Prospero magic", k=5, filters={"play": tempest_play})
    formatted_response = format_quotes_response(quotes_result)
    print(formatted_response)

def test_raw_search():
    """Test raw search to see what chunks we're getting."""
    
    print("\n🔍 Testing Raw Search Results")
    print("="*50)
    
    results = search_shakespeare("Prospero rough magic", k=5)
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Play: {result['metadata']['play']}")
        print(f"Act: {result['metadata']['act']}")
        print(f"Scene: {result['metadata']['scene_title']}")
        print(f"Characters: {result['metadata']['characters']}")
        print(f"Similarity: {1 - result['distance']:.3f}")
        print(f"Content Preview: {result['content'][:300]}...")
        print("-" * 50)

if __name__ == "__main__":
    test_raw_search()
    test_prospero_quotes()
    test_tempest_specific() 