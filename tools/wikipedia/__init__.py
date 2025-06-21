import wikipedia
from langchain.tools import tool
from .utils import identify_wikipedia_entities, extract_context, synthesize_information

no_relevant_info_found_sentence = "No relevant information could be found on Wikipedia about the query."

@tool
def wikipedia_page_retriever(query: str):
    """ Tool that fetches any pages from Wikipedia.

    Returns:
        String containing synthesized information useful to answer the query.
    """

    # Step 1: Analyze query and identify potential Wikipedia entities
    potential_entities = identify_wikipedia_entities(query)
    
    if not potential_entities:
        return no_relevant_info_found_sentence 
    
    # Step 2: Search Wikipedia for each identified entity
    for i, entity in enumerate(potential_entities):
        wikipedia_page = wikipedia.page(entity)
        if i == 0: context = extract_context(wikipedia_page)
        else: context += "\n\n" + extract_context(wikipedia_page)

    # Step 3: Synthesize information for the main agent
    # synthesized_info = synthesize_information(query, context)

    # if not synthesized_info:
    #     return no_relevant_info_found_sentence
    
    return context