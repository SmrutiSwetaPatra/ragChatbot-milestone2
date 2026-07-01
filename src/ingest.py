import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.scraper import load_documents
from src.chunker import chunk_documents
from src.vector_db import build_vector_db

def run_ingestion_pipeline():
    print("--- Starting Phase 2: Ingestion Pipeline ---")
    
    # 1. Scrape HTML content
    raw_docs = load_documents()
    if not raw_docs:
        print("No documents scraped. Exiting.")
        return
        
    # 2. Chunk text
    chunks = chunk_documents(raw_docs)
    
    # 3. Ingest into Vector DB
    build_vector_db(chunks)
    
    print("--- Phase 2 Pipeline Complete ---")

if __name__ == "__main__":
    run_ingestion_pipeline()
