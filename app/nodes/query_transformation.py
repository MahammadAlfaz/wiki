from app.core.llm import get_fast_llm
from app.graph.state import WikiState


def query_transformation_node(state:WikiState)->WikiState:
    question=state['question']
    llm=get_fast_llm()
    prompt = f"""
    You are an expert at reformulating DevOps and cloud infrastructure queries 
    for better search results in a technical knowledge base.

    Rewrite the following question to be more specific and search friendly.
    Focus on technical terms, project names, tools, and technologies.
    Return ONLY the rewritten query, nothing else.

    Examples:
    Input:  "How did we set up kubernetes for client X?"
    Output: "Kubernetes cluster setup configuration deployment client X GKE"

    Input:  "What went wrong during the AWS migration?"
    Output: "AWS migration issues problems errors troubleshooting"

    Original question: {question}

    Rewritten query:
    """
    result=llm.invoke(prompt)
    transformed=result.content.strip()

    print(f'Original query: {question}')
    print(f'Transformed query:{transformed}')

    return {'transformed_query':transformed}