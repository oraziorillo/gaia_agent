import re
from typing import Iterable
from langchain_core.documents import Document
from services.chroma import ChromaClient

chroma_client = ChromaClient()

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

def wikipedia_retriever(query: str):
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