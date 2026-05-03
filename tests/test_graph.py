from app.graph.rag_graph import rag_workflow

def test_graph_compiles():
    """Test 1 — graph compiles without errors."""
    print("✅ Graph compiled successfully!")
    print(rag_workflow.get_graph().draw_mermaid())

if __name__ == "__main__":
    test_graph_compiles()