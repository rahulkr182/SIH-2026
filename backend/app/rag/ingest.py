import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import Qdrant
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

def run_ingestion():
    # 1. Create dummy SOP file
    os.makedirs("data", exist_ok=True)
    sop_path = "data/mrpl_pipeline_sop.txt"
    with open(sop_path, "w") as f:
        f.write("""
MRPL Pipeline Safety and Operation Procedure (SOP)
Section 4: Carbon Steel Lines
For 6-inch carbon steel lines, the retirement thickness is defined strictly as 3.5mm.
Any line measuring below this threshold must be immediately decommissioned and flagged for replacement.

Section 5: Inspection Frequency
All carbon steel piping must undergo API 510 ultrasonic thickness inspection every 5 years.
""")

    print("Created mock SOP document.")

    # 2. Load and Chunk
    loader = TextLoader(sop_path)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    docs = text_splitter.split_documents(documents)
    
    # 3. Setup embeddings
    # Using FastEmbed for fast local embeddings without heavy torch downloads (BGE-small-en-v1.5)
    embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    
    # 4. Ingest into Qdrant
    qdrant_client = QdrantClient("http://localhost:6333")
    collection_name = "mrpl_sops"
    
    try:
        qdrant_client.get_collection(collection_name)
        print(f"Collection {collection_name} already exists.")
    except Exception:
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        print(f"Created collection {collection_name}.")

    Qdrant.from_documents(
        docs,
        embeddings,
        url="http://localhost:6333",
        collection_name=collection_name,
    )
    
    print("Ingestion complete. Added chunks to Qdrant.")

if __name__ == "__main__":
    run_ingestion()
