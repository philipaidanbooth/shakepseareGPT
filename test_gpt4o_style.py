#!/usr/bin/env python3
"""
Test script for GPT-4o style Shakespeare responses
"""

from shakespeare_rag import answer_with_shakespeare_context

def test_gpt4o_style_responses():
    """Test the GPT-4o style responses with specific questions."""
    
    # Questions similar to the Prospero example
    test_questions = [
        "What was the moment that Prospero wanted to leave his island in the Tempest?",
        "When does Hamlet decide to take action against Claudius?",
        "What is the turning point in Romeo and Juliet's relationship?",
        "How does Macbeth react when he first hears the witches' prophecy?",
        "What moment shows Othello's jealousy taking over?"
    ]
    
    print("🎭 GPT-4o Style Shakespeare Responses")
    print("="*60)
    
    for question in test_questions:
        print(f"\n🔍 Question: {question}")
        print("-" * 60)
        
        answer = answer_with_shakespeare_context(question, k=5)
        print(f"💡 Answer:\n{answer}")
        print("="*80)

def test_character_moments():
    """Test specific character moments and turning points."""
    
    character_moments = [
        "What is the moment when Lady Macbeth realizes her guilt?",
        "When does Juliet decide to take the potion?",
        "What is the exact moment when Iago convinces Othello of Desdemona's infidelity?",
        "When does King Lear realize his mistake about Cordelia?",
        "What is the turning point when Brutus decides to join the conspiracy?"
    ]
    
    print("\n👥 Character Moment Analysis")
    print("="*60)
    
    for moment in character_moments:
        print(f"\n🎭 Question: {moment}")
        print("-" * 60)
        
        answer = answer_with_shakespeare_context(moment, k=5)
        print(f"💡 Answer:\n{answer}")
        print("="*80)

def test_play_specific_questions():
    """Test questions about specific plays."""
    
    play_questions = [
        ("Hamlet", "What is the significance of the 'To be or not to be' soliloquy?"),
        ("Macbeth", "How does the 'Is this a dagger' scene reveal Macbeth's state of mind?"),
        ("Romeo and Juliet", "What does the balcony scene reveal about the lovers' relationship?"),
        ("Othello", "What is the significance of the handkerchief in Othello?"),
        ("King Lear", "What does Lear's 'Blow, winds' speech reveal about his character?")
    ]
    
    print("\n📚 Play-Specific Analysis")
    print("="*60)
    
    for play, question in play_questions:
        print(f"\n🎭 {play}: {question}")
        print("-" * 60)
        
        answer = answer_with_shakespeare_context(question, k=5, filters={"play": play})
        print(f"💡 Answer:\n{answer}")
        print("="*80)

if __name__ == "__main__":
    test_gpt4o_style_responses()
    test_character_moments()
    test_play_specific_questions() 