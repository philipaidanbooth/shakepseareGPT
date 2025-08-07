#!/usr/bin/env python3
"""
Debug script to find Prospero quotes in The Tempest
"""

from shakespeare_rag import search_shakespeare, extract_quotes_from_text, list_available_plays

def check_play_names():
    """Check what play names are actually in the database."""
    
    print("📚 Available Plays in Database:")
    print("="*50)
    
    plays = list_available_plays()
    for play in plays:
        print(f"  - {play}")
    
    # Look for Tempest specifically
    tempest_variations = [play for play in plays if "tempest" in play.lower()]
    print(f"\n🎭 Tempest variations found: {tempest_variations}")

def debug_tempest_quotes():
    """Debug what quotes we can find in The Tempest."""
    
    print("\n🔍 Debugging The Tempest Quotes")
    print("="*50)
    
    # First, find the exact play name
    plays = list_available_plays()
    tempest_play = None
    for play in plays:
        if "tempest" in play.lower():
            tempest_play = play
            break
    
    if not tempest_play:
        print("❌ The Tempest not found in database!")
        return
    
    print(f"✅ Found play: {tempest_play}")
    
    # Search for Prospero-related content
    queries = [
        "Prospero",
        "rough magic",
        "abjure",
        "break staff",
        "bury book",
        "Act V Scene I",
        "Tempest Act V"
    ]
    
    for query in queries:
        print(f"\n🔍 Searching for: '{query}'")
        print("-" * 40)
        
        results = search_shakespeare(query, k=3)
        
        for i, result in enumerate(results, 1):
            print(f"\n--- Result {i} ---")
            print(f"Play: {result['metadata']['play']}")
            print(f"Act: {result['metadata']['act']}")
            print(f"Scene: {result['metadata']['scene_title']}")
            print(f"Characters: {result['metadata']['characters']}")
            print(f"Similarity: {1 - result['distance']:.3f}")
            
            # Extract quotes from this result
            quotes = extract_quotes_from_text(result['content'])
            print(f"Quotes found: {len(quotes)}")
            for j, quote in enumerate(quotes[:3], 1):
                print(f"  {j}. {quote[:100]}...")
            
            print(f"Content preview: {result['content'][:200]}...")
            print("-" * 30)

def search_for_specific_quote():
    """Search for the specific 'rough magic' quote."""
    
    print("\n🎯 Searching for 'rough magic' quote specifically")
    print("="*50)
    
    # Try different variations
    variations = [
        "rough magic",
        "abjure",
        "But this rough magic",
        "I here abjure",
        "break my staff",
        "drown my book"
    ]
    
    for variation in variations:
        print(f"\n🔍 Searching: '{variation}'")
        results = search_shakespeare(variation, k=2)
        
        for result in results:
            if "tempest" in result['metadata']['play'].lower():
                print(f"Found in: {result['metadata']['play']} - {result['metadata']['act']} - {result['metadata']['scene_title']}")
                print(f"Content: {result['content'][:300]}...")
                print("-" * 30)

def test_with_correct_play_name():
    """Test with the correct play name format."""
    
    print("\n🎭 Testing with correct play name")
    print("="*50)
    
    # Find the exact Tempest play name
    plays = list_available_plays()
    tempest_play = None
    for play in plays:
        if "tempest" in play.lower():
            tempest_play = play
            break
    
    if tempest_play:
        print(f"Testing with play name: {tempest_play}")
        
        # Test the filtering with the correct play name
        from shakespeare_rag import get_quotes_from_chunks, format_quotes_response
        
        quotes_result = get_quotes_from_chunks("Prospero magic", k=5, filters={"play": tempest_play})
        formatted_response = format_quotes_response(quotes_result)
        print(formatted_response)
    else:
        print("❌ The Tempest not found in database!")

if __name__ == "__main__":
    check_play_names()
    debug_tempest_quotes()
    search_for_specific_quote()
    test_with_correct_play_name() 