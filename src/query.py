import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.rag_pipeline import generate_response

def main():
    if len(sys.argv) < 2:
        print("Usage: python src/query.py \"<your question here>\"")
        sys.exit(1)
        
    query = " ".join(sys.argv[1:])
    print(f"Executing RAG pipeline for query: '{query}'...")
    
    result = generate_response(query)
    
    print("\n" + "="*50)
    print("FINAL ANSWER:")
    print("="*50)
    print(result['answer'])
    
    if result.get('sources'):
        print("\nSOURCES:")
        for s in result['sources']:
            print(f"- {s}")
    print("="*50)

if __name__ == "__main__":
    main()
