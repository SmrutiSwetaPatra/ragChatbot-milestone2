import sys
import os
from typing import List
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document

# Add parent dir to sys.path to import config if run standalone
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import src.config as config

def load_documents() -> List[Document]:
    """
    Scrapes the configured Groww URLs and returns Langchain Document objects.
    Extracts text from the HTML but does NOT process any PDFs as per constraints.
    """
    print(f"Loading documents from {len(config.SCHEME_URLS)} URLs...")
    
    docs = []
    for url in config.SCHEME_URLS:
        try:
            print(f"Scraping {url}...")
            # WebBaseLoader uses urllib and BeautifulSoup under the hood
            loader = WebBaseLoader(url)
            # The loader will extract the main text of the webpage
            page_docs = loader.load()
            
            # Enrich metadata
            for doc in page_docs:
                doc.metadata['source_url'] = url
                # Extract scheme name from the URL string
                scheme_name = url.split('/')[-1].replace('-', ' ').title()
                doc.metadata['scheme_name'] = scheme_name
                
            docs.extend(page_docs)
            print(f"Successfully loaded content from {url}")
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            
    print(f"Total documents loaded: {len(docs)}")
    return docs

if __name__ == "__main__":
    loaded_docs = load_documents()
    for d in loaded_docs:
        print(f"Scheme: {d.metadata.get('scheme_name')} | Content Length (chars): {len(d.page_content)}")
