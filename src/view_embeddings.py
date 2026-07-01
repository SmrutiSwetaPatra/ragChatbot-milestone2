import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.vector_db import get_vector_db

def view_embeddings():
    print("Loading Vector Database from ChromaDB...")
    db = get_vector_db()
    
    print("Retrieving chunks and their embeddings...")
    # Get all items from the collection, including the actual vector embeddings
    collection_data = db.get(include=["embeddings", "documents", "metadatas"])
    
    ids = collection_data.get("ids", [])
    embeddings = collection_data.get("embeddings", [])
    documents = collection_data.get("documents", [])
    metadatas = collection_data.get("metadatas", [])
    
    if not ids:
        print("No embeddings found in the database. Has the ingestion script finished?")
        return
        
    print(f"Total embedded chunks found: {len(ids)}")
    print(f"Embedding Vector Dimension: {len(embeddings[0])}")
    
    output_data = []
    for i in range(len(ids)):
        output_data.append({
            "chunk_id": ids[i],
            "scheme_name": metadatas[i].get("scheme_name", "Unknown"),
            "content_preview": documents[i][:150].replace('\n', ' ') + "...",
            "vector_dimension": len(embeddings[i]),
            "full_embedding_vector": embeddings[i].tolist() if hasattr(embeddings[i], 'tolist') else list(embeddings[i]) # Fix numpy JSON serialization
        })
        
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "embeddings_verification.json")
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4)
        
    print(f"Verification data (including FULL embeddings) saved to {output_path}")

if __name__ == "__main__":
    view_embeddings()
