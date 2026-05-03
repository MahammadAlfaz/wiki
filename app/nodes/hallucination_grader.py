from app.core.llm import get_fast_llm
from app.graph.state import WikiState


def hallucination_grader_node(state:WikiState)->WikiState:
    llm=get_fast_llm()
    answer=state['generated_answer']
    docs=state['graded_docs']
    question=state['question']

    if not docs:
        return{
            'hallucination_score':0.0
        }
    if "don't have enough information" in answer.lower():
        return {
            "hallucination_score":0.0
        }
    context = "\n\n".join([
        f"Source — {docs[i].metadata.get('source', 'unknown').split('/')[-1]}:\n{docs[i].page_content}"
        for i in range(len(docs))
    ])
    prompt = f"""
    You are a technical fact checker for a DevOps knowledge base.

    Check if the answer is fully supported by the provided context.
    Pay special attention to:
    - Technical commands and configurations
    - Service names and versions
    - Project specific details
    - Architecture decisions

    Score between 0.0 and 1.0:
    1.0 → every claim is supported by context
    0.7 → most claims supported, minor gaps
    0.5 → some claims supported, some not
    0.0 → answer not supported by context at all

    Return ONLY a number between 0.0 and 1.0, nothing else.

    Context:
    {context}

    Question: {question}

    Answer to check:
    {answer}

    Score:
    """
    result=llm.invoke(prompt)

    try:
        score=float(result.content.strip())
        score=max(0.0,min(1.0,score))
    except ValueError:
        score=0.0
    

    print(f'hallucination score: {score}')
    return {
        'hallucination_score':score
    }
