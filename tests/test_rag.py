import sys
sys.path.append(".")

from app.graph.rag_graph import rag_workflow


def test_rag_pipeline():
    """Test 4 — end to end RAG pipeline."""

    result = rag_workflow.invoke({
        "question": "How did we set up Kubernetes for project X?",
        "user_id": "test-user",
        "user_role": "engineer",
        "transformed_query": "",
        "should_retrieve": True,
        "retrieved_docs": [],
        "graded_docs": [],
        "web_search_used": False,
        "generated_answer": "",
        "hallucination_score": 0.0,
        "attempts": 0,
        "final_answer": "",
        "sources": []
    })

    print(f"\nQuestion: How did we set up Kubernetes for project X?")
    print(f"Answer: {result['final_answer']}")
    print(f"Sources: {result['sources']}")
    print(f"Hallucination score: {result['hallucination_score']}")
    print(f"Web search used: {result['web_search_used']}")
    print(f"Attempts: {result['attempts']}")
    print("✅ RAG pipeline test passed!")


if __name__ == "__main__":
    test_rag_pipeline()