import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.rag.retriever import retrieve_relevant_chunks


def evaluate_retrieval():
    test_cases = [
        {
            "question": "What is the difference between L1 and L2 regularization?",
            "expected_keywords": ["L1", "L2", "regularization", "Laplacean", "Gaussian"],
        },
        {
            "question": "What is overfitting?",
            "expected_keywords": ["overfitting", "training", "generalize"],
        },
        {
            "question": "What is the difference between supervised and unsupervised learning?",
            "expected_keywords": ["supervised", "unsupervised", "labeled"],
        },
        {
            "question": "What is a decision tree?",
            "expected_keywords": ["decision tree", "tree structure"],
        },
        {
            "question": "What is RNN?",
            "expected_keywords": [],
        },
    ]
    
    print("=" * 80)
    print("Evaluating Retrieval Quality")
    print("=" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        question = test_case["question"]
        expected_keywords = test_case["expected_keywords"]
        
        print(f"\n{'─'*80}")
        print(f"Test {i}: {question}")
        print(f"{'─'*80}")
        
        chunks = retrieve_relevant_chunks(question, top_k=5)
        all_text = " ".join([chunk["text"] for chunk in chunks])
        
        found_keywords = []
        missing_keywords = []
        
        for keyword in expected_keywords:
            if keyword.lower() in all_text.lower():
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)

        print(f"\nRetrieved {len(chunks)} chunks")
        print(f"Average distance: {sum(c['distance'] for c in chunks) / len(chunks):.4f}")
        
        if expected_keywords:
            print(f"\nExpected keywords: {', '.join(expected_keywords)}")
            print(f"Found keywords: {', '.join(found_keywords) if found_keywords else 'None'}")
            print(f"Missing keywords: {', '.join(missing_keywords) if missing_keywords else 'None'}")
            
            if len(found_keywords) / len(expected_keywords) >= 0.6:
                print("✓ GOOD: Most expected keywords found")
            else:
                print("⚠ WARNING: Many expected keywords not found")
        else:
            print("\nNo expected keywords (question should not be answerable)")
            print("✓ Model should say 'I don't have enough information'")
    
    print(f"\n{'='*80}")
    print("Evaluation Complete")
    print("=" * 80)


if __name__ == "__main__":
    evaluate_retrieval()