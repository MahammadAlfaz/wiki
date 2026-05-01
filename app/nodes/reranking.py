from app.core.llm import get_fast_llm
from app.graph.state import WikiState


def reranking_node(state:WikiState)->WikiState:
    llm=get_fast_llm()
    question=state['question']
    docs=state['retrieved_docs']

    if not docs:
        print("No docs to rerank")
        return {"retrieved_docs":[]}
    scored_docs=[]

    for doc in docs:
        source=doc.metadata.get('source','unknown')
        file_name=source.split('/')[-1] if "/" in source else source 
        prompt = f"""
        You are evaluating document relevance for a DevOps knowledge base.
        
        Score how relevant this document chunk is to the query.
        Consider: technical terms match, project context, 
                  specific tools/services mentioned.
        
        Return ONLY a number between 0.0 and 1.0.
        
        Query: {question}
        
        Document (from {file_name}):
        {doc.page_content[:500]}
        
        Relevance score (0.0 to 1.0):
        """
        result=llm.invoke(prompt)

        try:
            score=float(result.content.strip())
            score=max(0.0,min(1.0,score))
        except ValueError:
            score=0.0
        print(f"Score: {score} | Source:{file_name} | {doc.page_content[:60]}...")
        
        scored_docs.append((score,doc))
    scored_docs.sort(key=lambda x:x[0],reverse=True)

    top_docs=[doc for score ,doc in scored_docs[:3]]
    print(f"Top {len(top_docs)} does after reranking ")
    return {
        'retrieved_docs':top_docs
    }

