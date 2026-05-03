from dotenv import load_dotenv
from langchain_community.tools import TavilySearchResults
from langchain_core.documents import Document
from app.graph.state import WikiState


load_dotenv()

def web_search_node(state:WikiState)->WikiState:
    """
    Fallback when no relevant docs found in knowledge base.
    Searches web for general Devops information 
    Note:Web results are clearly marked so engineer know 
    this came from web, not internal POC docs
    """

    question=state['transformed_query']
    print(f'No relavant docs found - searching web for: {question}')
    try:
        web_search_tool=TavilySearchResults(
            max_results=3
        )
        results=web_search_tool.invoke(question)
        web_docs=[
            Document(
                page_content=result['content'],
                metadata={
                    'source':result['url'],
                    'type':'web_search',
                    'web_search':True
                }
            )
            for result in results
            if result.get('content')
        ]
        print (f'web search returned {len(web_docs)} docs')

        return {
            'graded_docs':web_docs,
            'web_search_used':True,
            'sources':[r['url'] for r in results if r.get('url')]
        }
    except Exception as e:
        print (f"Web search failed:{e}")
        return {
            'graded_docs':[],
            'web_search_used':True,
            'sources':[]
        }
