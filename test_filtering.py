#!/usr/bin/env python3
"""
Test script for play filtering functionality
"""

from shakespeare_rag import answer_with_shakespeare_context, list_available_plays

def test_play_filtering():
    """Test play filtering with different plays."""
    
    print("🎭 Testing Play Filtering")
    print("="*50)
    
    # First, let's see what plays are available
    plays = list_available_plays()
    print(f"📚 Available plays: {len(plays)}")
    print("First 10 plays:")
    for i, play in enumerate(plays[:10], 1):
        print(f"  {i}. {play}")
    
    # Test filtering with specific plays
    test_cases = [
        {
            "play": "Hamlet",
            "question": "What does Hamlet say about death?",
            "description": "Hamlet death quote"
        },
        {
            "play": "Macbeth", 
            "question": "How does Macbeth react to the witches?",
            "description": "Macbeth witches reaction"
        },
        {
            "play": "Romeo and Juliet",
            "question": "How does Romeo describe Juliet?",
            "description": "Romeo Juliet description"
        }
    ]
    
    for test_case in test_cases:
        play_name = test_case["play"]
        question = test_case["question"]
        description = test_case["description"]
        
        print(f"\n🔍 Testing: {description}")
        print(f"🎭 Play: {play_name}")
        print(f"❓ Question: {question}")
        print("-" * 50)
        
        try:
            # Test with play filter
            answer = answer_with_shakespeare_context(
                question, 
                k=3, 
                filters={"play": play_name}
            )
            print(f"💡 Answer:\n{answer}")
        except Exception as e:
            print(f"❌ Error with {play_name}: {e}")
        
        print("="*80)

def test_filtering_syntax():
    """Test the filtering syntax specifically."""
    
    print("\n🔧 Testing Filtering Syntax")
    print("="*50)
    
    from shakespeare_rag import search_shakespeare
    
    # Test different filter combinations
    filter_tests = [
        {"play": "Hamlet"},
        {"play": "Macbeth"},
        {"play": "Romeo and Juliet"},
        {"characters": "HAMLET"},
        {"characters": "MACBETH"}
    ]
    
    for filters in filter_tests:
        print(f"\n🔍 Testing filters: {filters}")
        try:
            results = search_shakespeare("death", k=2, filters=filters)
            print(f"✅ Found {len(results)} results")
            for i, result in enumerate(results, 1):
                metadata = result['metadata']
                similarity = 1 - result['distance']
                print(f"  {i}. {metadata['play']} - {metadata['act']} - {metadata['scene_title']} (Relevance: {similarity:.3f})")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_play_filtering()
    test_filtering_syntax() 