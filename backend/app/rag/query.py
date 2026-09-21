import os
from langchain_qdrant import Qdrant
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from qdrant_client import QdrantClient

def search_sops(query: str, top_k: int = 3) -> str:
    """
    Searches the Qdrant DB for relevant SOP chunks based on the natural language query.
    Returns a formatted string of the retrieved contexts.
    """
    embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key = os.getenv("QDRANT_API_KEY", None)
    
    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
    
    qdrant = Qdrant(
        client=client,
        collection_name="mrpl_sops",
        embeddings=embeddings
    )
    
    docs = qdrant.similarity_search(query, k=top_k)
    
    if not docs:
        return "No relevant SOPs found."
        
    context = "\n\n".join([f"Document Context: {doc.page_content}" for doc in docs])
    return context
