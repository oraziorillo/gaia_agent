from typing import List
from wikipedia import WikipediaPage
from bs4 import BeautifulSoup
from html_to_markdown import convert_to_markdown
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai.chat_models import ChatOpenAI
from .prompts import entity_analysis_prompt, synthesis_prompt

chat_model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0, 
    seed=42,
    top_p=0.95 
)

def identify_wikipedia_entities(query: str) -> List[str]:
    """
    Use LLM to analyze the query and identify potential Wikipedia entities.
    
    Args:
        query: The input query to analyze
        
    Returns:
        List of potential Wikipedia page titles
    """
    prompt = PromptTemplate.from_template(entity_analysis_prompt)
    chain = prompt | chat_model | StrOutputParser()
    response = chain.invoke({'query': query})
    
    if "NONE" in response.upper():
        return []
    
    entities = []

    # Parse the response to extract entities
    for entity in response.strip().split(';'):
        entities.append(entity.strip())
    
    return entities

def extract_context(page: WikipediaPage):
    html_page = page.html()
    clean_html_page = clean_wikipedia_html(html_page)
    md_page = convert_to_markdown(clean_html_page)
    return f"# {page.title}\n\n{md_page}\n\n---"

def synthesize_information(query: str, context: str) -> str:
    """
    Use LLM to synthesize Wikipedia information relevant to the original query.
    
    Args:
        original_query: The original complex query
        wikipedia_results: List of Wikipedia page results
        
    Returns:
        Synthesized information or "I have found no information."
    """

    prompt = PromptTemplate.from_template(synthesis_prompt) 
    chain = prompt | chat_model | StrOutputParser()
    response = chain.invoke({'query': query, 'context': context})
    
    if not response:
        return None
    
    return response.strip()
    
def clean_wikipedia_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    # 1. Remove all <style> tags
    for style_tag in soup.find_all("style"):
        style_tag.decompose()

    # 2. Remove all elements with role="navigation"
    for nav_tag in soup.find_all(attrs={"role": "navigation"}):
        nav_tag.decompose()

    # 3. Remove all <figure> tags
    for figure in soup.find_all("figure"):
        figure.decompose()

    # 4. Flatten all <a> tags (replace with their text)
    for a in soup.find_all("a"):
        a.replace_with(a.get_text())

    return str(soup)