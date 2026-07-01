import sys
import os
from typing import List
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import src.config as config

def get_embedding_model():
    """Initializes and returns the BGE embedding model."""
    print(f"Loading embedding model: {config.EMBEDDING_MODEL_NAME}...")
    # BGE models perform best with normalized embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name=config.EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'}, 
        encode_kwargs={'normalize_embeddings': True} 
    )
    return embeddings

def build_vector_db(docs: List[Document]):
    """
    Takes chunked documents, embeds them using BGE, and stores them in ChromaDB.
    """
    embedding_model = get_embedding_model()
    
    print(f"Initializing Chroma vector store at {config.VECTOR_DB_DIR}...")
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embedding_model,
        persist_directory=config.VECTOR_DB_DIR,
        collection_name="mutual_fund_faqs"
    )
    
    print(f"Successfully ingested {len(docs)} document chunks into the Vector DB.")
    return vectorstore

def get_vector_db():
    """Returns the initialized Vector DB for querying."""
    embedding_model = get_embedding_model()
    vectorstore = Chroma(
        persist_directory=config.VECTOR_DB_DIR,
        embedding_function=embedding_model,
        collection_name="mutual_fund_faqs"
    )
    return vectorstore
