from app.core.llm import get_llm
from app.graph.state import WikiState


def grade_docs_node(state:WikiState)->WikiState:
    llm=get_llm()
    question=state['question']
    docs=state['retrieved_docs']

    if not docs:
        print('No docs to grade')
        return {
            "graded_docs":[],
            "source":[]
        }
    relavant_docs=[]
    sources=[]

    for doc in docs:
        source=doc.metadata.get('source','unknown')
        file_name=source.split('/')[-1] if"/" in source else source

        prompt = f"""
        You are grading document relevance for a DevOps knowledge base.

        Return ONLY "relevant" or "irrelevant".

        A document is relevant if it:
        - Directly answers the query
        - Contains related technical information
        - Mentions the same project, tool, or service
        - Contains useful context for the query

        A document is irrelevant if it:
        - Talks about completely different projects
        - Contains unrelated technical content
        - Has no connection to the query topic

        Query: {question}

        Document (from {file_name}):
        {doc.page_content[:500]}

        Grade (relevant/irrelevant):
        """

        result=llm.invoke(prompt)
        grade=result.content.strip().lower()

        if 'relavant' in grade and 'irrelavant' not in grade :
            relavant_docs.append(doc)
            sources.append(file_name)
            print(f'RELEVANT: {file_name} | {doc.page_content[:60]}...')
        else:
            print(f"IRRELEVANT: {file_name} | {doc.page_content[:60]}")
    sources=list(set(sources))
    print(f"Relavant docs: {len(relavant_docs)}/{len(docs)}")
    print(f"Sources: {sources}")
    return {
        "graded_docs" :relavant_docs,
        'source':sources
    }
