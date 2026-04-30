from app.core.llm import get_llm
from app.graph.state import WikiState


def should_retrieve_node(state:WikiState)->WikiState:
    llm=get_llm()
    question=state['transformed_query']
    prompt = f"""
    You are a router for a DevOps knowledge base.
    
    Decide if this query needs document retrieval.
    Return ONLY "yes" or "no".

    "yes" → technical questions about:
            deployments, configurations, architecture,
            GCP/AWS/Azure services, Kubernetes, Docker,
            CI/CD pipelines, migrations, incidents, POCs,
            project specific questions

    "no"  → greetings, general conversation,
             simple definitions available without docs

    Query: {question}

    Answer (yes/no):
    """
    result=llm.invoke(prompt)
    decision=result.content.strip()
    should_retrieve="yes" in decision

    print(f"Should_retrieve: {should_retrieve}")
    return {
        'should_retrieve':should_retrieve,
        'attempts':0
    }

    