from langchain_community.retrievers import WikipediaRetriever
from langchain.tools import tool

retriever = WikipediaRetriever()

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

chain = retriever | format_docs

@tool
def wikipedia_retriever_tool(query: str):
    """ Run a query to the Wikipedia API through a natural language query. """
    return chain.invoke(query) 

print("Imported wikipedia_retriever tool.")