from app.core.llm import get_llm
from app.graph.state import WikiState


def generate_answer_node(state:WikiState)->WikiState:
    llm=get_llm()
    question=state['question']
    docs=state['graded_docs']
    attempts=state['attempts']
    sources=state['sources']
    should_retrieve=state['should_retrieve']

    if attempts >=3:
        return {
            'generated_answer':"I don't have enough information to answer this accurately. Please check with the admin for the answer",
            'attempts':attempts,
            'final_answer':"I don't have enough information to answer this accurately. Please check with the admin for the answer"
        }
    if not should_retrieve:
        results=llm.invoke(question)
        answer=results.content.strip()
        return {
            'generated_answer':answer,
            'attempts':attempts+1,
            'final_answer':answer
        }
    if not docs:
        return{
            'generated_answer':"I don't have enough information to answer this accurately",
            'attempts':attempts+1,
            'final_answer':"I don't have enough information to answer this accurately"
        }
    context = "\n\n".join([
        f"Source — {docs[i].metadata.get('source', 'unknown').split('/')[-1]}:\n{docs[i].page_content}"
        for i in range(len(docs))
    ])
    prompt = f"""
    You are a DevOps knowledge base assistant at Niveus Solutions.
    
    Your job is to answer questions about internal projects, 
    POCs, deployments, and infrastructure based ONLY on the 
    provided documentation.

    Rules:
    - Answer ONLY from the provided context
    - Be specific and technical — this is for DevOps engineers
    - Include relevant commands, configs, or steps if present in context
    - If answer is partially available, share what you know and mention gaps
    - If context doesn't contain the answer, say 
      "I don't have enough information to answer this accurately."
    - NEVER make up technical details, commands, or configurations
    - Always mention which document the information comes from

    Context:
    {context}

    Question: {question}

    Answer:
    """
    result=llm.invoke(prompt)
    answer=result.content.strip()
    print(f" Generated answer (attempt {attempts+1}): {answer[:100]}...")
    if "don't have enough information" in answer.lower():
        return {
            'generated_answer':answer,
            'attempts':attempts+1,
            'final_answer':answer
        }
    return {
        'generated_answer':answer,
        'attempts':attempts +1,
        'final_answer':answer
    }

