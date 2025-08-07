#!/usr/bin/env python3
"""
Simple test script for the simplified Shakespeare RAG system
"""

from shakespeare_rag import answer_with_shakespeare_context

def test_simple_questions():
    """Test simple questions with the simplified system."""
    
    print("🎭 Testing Simplified Shakespeare RAG System")
    print("="*50)
    
    test_questions = [
        "What does Hamlet say about death?",
        "How does Romeo describe Juliet?",
        "What is Macbeth's reaction to the witches' prophecy?"
    ]
    
    for question in test_questions:
        print(f"\n🔍 Question: {question}")
        print("-" * 40)
        
        try:
            answer = answer_with_shakespeare_context(question, k=3)
            print(f"💡 Answer:\n{answer}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("="*80)

if __name__ == "__main__":
    test_simple_questions() 