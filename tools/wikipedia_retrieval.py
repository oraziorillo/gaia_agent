import re
import wikipedia
from bs4 import BeautifulSoup
from typing import Iterable
from langchain_core.documents import Document
from services.chroma import ChromaClient

# Similarity retriever
pages_cache: dict[str, wikipedia.WikipediaPage] = {}
chroma_client = ChromaClient()

def wikipedia_page_search(query: str):
    return wikipedia.search(query)
    
def wikipedia_page_sections_retriever(page_title: str):
    try:
        page = wikipedia.page(title=page_title, auto_suggest=False)
        pages_cache[page.title] = page
        return "Page title: " + page.title + "\nSections:" + str(_get_page_sections(page))
    except wikipedia.DisambiguationError as e:
        return "Disambiguation required. Call this tool again with one of the following options: " + str(e.options)

def wikipedia_section_content_retriever(page_title: str, section_title: str):
    try:
        page = pages_cache[page_title]
        return page.section(section_title)
    except KeyError:
        return "Page not found in cache. Please use the correct page title as returned by the wikipedia_page_sections_retriever tool."
    
def wikipedia_similarity_retriever(query: str):
    data = _load_wikipedia_data(query)
    chunks = _split_text_into_chunks(data)

    ids, documents, metadatas = [], [], []
    for chunk in chunks:
        ids.append(str(hash(chunk.page_content)))
        documents.append(chunk.page_content)
        metadatas.append(chunk.metadata)
    
    collection_name = re.sub('[^A-Za-z0-9 ]+', '', query).replace(" ", "_").lower()
    chroma_client.create_or_get_collection(collection_name)
    chroma_client.add_documents(
        collection_name=collection_name,
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    results = chroma_client.query_collection(
        collection_name=collection_name,
        query=query,
        n_results=10
    )
    chroma_client.delete_collection(collection_name)

    return "\n\n".join(results)

def _get_page_sections_from_html(page_html: str) -> list[str]:
    soup = BeautifulSoup(page_html, 'html.parser')
    h2s = soup.find_all('h2')
    return [h2.text for h2 in h2s]

def _get_page_sections(page: wikipedia.WikipediaPage):
    if page.sections:
        return str(page.sections)
    else:
        return _get_page_sections_from_html(page.html())
    
def _load_wikipedia_data(query: str, lang: str = 'en', load_max_docs: int = 2):
    from langchain_community.document_loaders import WikipediaLoader
    loader = WikipediaLoader(query=query, lang=lang, load_max_docs=load_max_docs)
    data = loader.load()
    return data

def _split_text_into_chunks(data: Iterable[Document], chunk_size=512):
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=0)
    chunks = text_splitter.split_documents(data)
    return chunks
