from typing import Any, List, Mapping, Optional

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from chromadb.errors import NotFoundError

# This class works with a local Chroma DB hosted on port 8000 with docker.
# To set it up, just run the command: 
# > docker run -v ./chroma-data:/data -p 8000:8000 chromadb/chroma
# or run it with custom config via 
# > docker run -v ./chroma-data:/data -v ./config.yaml:/config.yaml -p 8000:8000 chromadb/chroma
# after setting up the .config.yaml file

class ChromaClient:
    def __init__(self):
        self.client = chromadb.HttpClient(host='localhost', port=8000)

    def create_or_get_collection(self, collection_name: str) -> str:
        """ Creates a new Chroma collection with the given name if a collection with that name doesn't exist
        or gets the existing collection with that name.

        Returns:
            str - the name of the collection just created
        """
        try:
            collection = self.client.get_collection(name=collection_name)
        except NotFoundError:
            collection = self.client.create_collection(
                name=collection_name,
                embedding_function=OpenAIEmbeddingFunction(
                    model_name="text-embedding-3-small"
                )
            )
        return collection.name

    def add_documents(
        self, 
        collection_name: str, 
        ids: List[int], 
        documents: List[str], 
        metadatas: Optional[Mapping[str, Any]] = None
    ):
        self.client.get_collection(name=collection_name).add(
            ids=ids, 
            documents=documents, 
            metadatas=metadatas,
        )

    def query_collection(self, collection_name: str, query: str, n_results: int = 5) -> List[str]:
        results: chromadb.QueryResult = self.client.get_collection(collection_name).query(
            query_texts=[query],
            n_results=n_results
        )
        return results['documents']          

    def delete_collection(self, collection_name):
        self.client.delete_collection(collection_name)