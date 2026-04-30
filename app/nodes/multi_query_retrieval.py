from typing import Set

from app.core.llm import get_fast_llm
from app.graph.state import WikiState
from app.rag.retriever import get_retriever


def multi_query_retrieval_node(state:WikiState)->WikiState:
    llm=get_fast_llm()
    transformed_query=state['transformed_query']
    original_question=state['question']

    prompt = f"""
    You are an expert at generating search queries for a DevOps 
    knowledge base containing POC documents, deployment guides, 
    architecture docs, and incident reports.

    Generate 3 different search queries to find relevant documents.
    Each query should focus on a different aspect.
    Return ONLY the 3 queries, one per line, no numbering, no extra text.

    Examples of good queries for DevOps knowledge base:
    - "GKE cluster node pool configuration autopilot"
    - "terraform deployment pipeline CI/CD Jenkins"
    - "incident postmortem database migration failure"

    Topic: {transformed_query}

    Queries:
    """

    result=llm.invoke(prompt)
    queries=[
        q.strip()
        for q in result.content.strip().split("\n")
        if q.strip()
        
    ][:3]
    queries=[original_question]+queries

    print(f'Generated queries: {queries} ')

    retriever=get_retriever(k=3)
    seen_content=Set()
    all_docs=[]

    for query in queries:
        try:
            docs=retriever.invoke(query)
            for doc in docs:
                if doc.page_content not in seen_content:
                    seen_content.add(doc.page_content)
                    all_docs.append(doc.page_content)
        except Exception as e:
            print(f"Retriveal error for query '{query}':'{e}'")
    print(f"Total unique docs retrived: len(all_docs)")
    return {
        'retrieved_docs':all_docs
    }