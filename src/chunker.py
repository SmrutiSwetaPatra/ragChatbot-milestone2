import sys
import os
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Add parent dir to sys.path to import config if run standalone
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import src.config as config
from src.scraper import load_documents

def chunk_documents(docs: List[Document]) -> List[Document]:
    """
    Takes a list of Langchain Document objects and splits them into smaller chunks 
    based on the configured CHUNK_SIZE and CHUNK_OVERLAP.
    Metadata from the original documents is preserved in the chunks.
    """
    print(f"Initializing text splitter with chunk_size={config.CHUNK_SIZE} and overlap={config.CHUNK_OVERLAP}...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )
    
    print(f"Splitting {len(docs)} documents into chunks...")
    chunked_docs = text_splitter.split_documents(docs)
    
    print(f"Successfully generated {len(chunked_docs)} chunks.")
    return chunked_docs

if __name__ == "__main__":
    # Test the chunker
    raw_docs = load_documents()
    chunks = chunk_documents(raw_docs)
    
    if chunks:
        print("\n--- Sample Chunk ---")
        print(f"Scheme: {chunks[0].metadata.get('scheme_name')}")
        print(f"URL: {chunks[0].metadata.get('source_url')}")
        print(f"Content Length (chars): {len(chunks[0].page_content)}")
        print(f"Preview: {chunks[0].page_content[:100]}...")
