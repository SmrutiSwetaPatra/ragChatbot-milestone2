import os
import sys
import json

# Add parent dir to sys.path to import config if run standalone
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.scraper import load_documents
from src.chunker import chunk_documents

def main():
    print("Starting data extraction and chunking process...")
    
    # 1. Load documents via scraper
    raw_docs = load_documents()
    
    if not raw_docs:
        print("No documents were loaded. Exiting.")
        return
        
    # 2. Chunk the documents
    chunks = chunk_documents(raw_docs)
    
    # 3. Serialize to JSON for user review
    output_data = []
    for i, chunk in enumerate(chunks):
        output_data.append({
            "chunk_id": i + 1,
            "scheme_name": chunk.metadata.get("scheme_name", "Unknown"),
            "source_url": chunk.metadata.get("source_url", "Unknown"),
            "content_length": len(chunk.page_content),
            "content": chunk.page_content
        })
        
    output_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "chunks.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
        
    print(f"\nSuccessfully saved {len(chunks)} chunks to {output_file}")
    print("You can review this file to ensure the scraping and chunking extracted the correct data.")

if __name__ == "__main__":
    main()
