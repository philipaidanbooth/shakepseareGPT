#!/usr/bin/env python3
"""
Test script for Shakespeare Quotes functionality
"""

from shakespeare_rag import get_quotes_from_chunks, format_quotes_response

def test_quotes_functionality():
    """Test the quotes functionality with various queries."""
    
    test_queries = [
        "To be or not to be",
        "Romeo and Juliet love",
        "Macbeth ambition",
        "Hamlet's madness",
        "Lady Macbeth's guilt"
    ]
    
    print("🎭 Shakespeare Quotes Test")
    print("="*50)
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 40)
        
        # Get quotes without filters
        quotes_result = get_quotes_from_chunks(query, k=3)
        formatted_response = format_quotes_response(quotes_result)
        print(formatted_response)
        
        # Test with play filter
        print(f"\n🔍 Query: '{query}' (filtered to Hamlet only)")
        quotes_result_filtered = get_quotes_from_chunks(query, k=3, filters={"play": "Hamlet"})
        formatted_response_filtered = format_quotes_response(quotes_result_filtered)
        print(formatted_response_filtered)
        
        print("="*80)

def test_character_specific_quotes():
    """Test quotes for specific characters."""
    
    characters = ["HAMLET", "ROMEO", "MACBETH", "JULIET", "LADY MACBETH"]
    
    print("\n👥 Character-Specific Quotes Test")
    print("="*50)
    
    for character in characters:
        print(f"\n🔍 Character: {character}")
        print("-" * 40)
        
        quotes_result = get_quotes_from_chunks(f"{character} quotes", k=3, filters={"characters": character})
        formatted_response = format_quotes_response(quotes_result)
        print(formatted_response)
        
        print("="*80)

if __name__ == "__main__":
    test_quotes_functionality()
    test_character_specific_quotes() 