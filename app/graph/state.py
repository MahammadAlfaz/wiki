
from typing import List, TypedDict


class WikiState(TypedDict):
    question:str
    user_id:str
    user_role:str

    transformed_query:str
    should_retrieve:bool
    retrieved_docs:List
    graded_docs:List
    web_search_used:bool
    generated_answer:str
    hallucination_score:float
    attempts:int

    final_answer:str
    sources:List[str]
