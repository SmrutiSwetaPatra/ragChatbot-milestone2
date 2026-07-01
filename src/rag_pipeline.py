import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import src.config as config
from src.vector_db import get_vector_db
from src.guardrails import process_query_input
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from tenacity import retry, stop_after_attempt, wait_exponential
from datetime import date

# Strict System Prompt
SYSTEM_PROMPT = """You are a helpful, strictly factual Mutual Fund FAQ assistant.
Your goal is to answer the user's question using ONLY the provided context from the official Groww mutual fund pages.
Do not use outside knowledge. If the answer is not in the context, explicitly say: "I'm sorry, but I don't have that information based on the provided data."
Never provide investment advice or recommendations.
Limit your response to a maximum of 3 sentences.

Context:
{context}

Question:
{question}

Answer:"""

def generate_response(query: str):
    """
    Executes the full RAG pipeline:
    1. Guardrails
    2. Retrieval
    3. LLM Generation
    """
    print(f"\n[User Query]: {query}")
    
    # Step 1: Guardrails
    guardrail_result = process_query_input(query)
    if not guardrail_result["is_safe"]:
        print("[Guardrail]: Query blocked. Returning safe response.")
        return {
            "answer": guardrail_result["response"],
            "sources": []
        }
    
    clean_query = guardrail_result["query"]
    
    # Step 2: Retrieval
    print("[Retrieval]: Searching Vector DB for relevant context...")
    db = get_vector_db()
    retriever = db.as_retriever(search_kwargs={"k": 3})
    retrieved_docs = retriever.invoke(clean_query)
    
    if not retrieved_docs:
        return {
            "answer": "I'm sorry, I could not find any relevant information to answer your question.",
            "sources": []
        }
        
    context_text = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
    
    # Extract unique sources for citations
    sources = list(set([doc.metadata.get("source_url", "Unknown Source") for doc in retrieved_docs]))
    
    # Step 3: LLM Generation
    print("[Generation]: Asking the LLM...")
    if not config.GROQ_API_KEY:
        return {
            "answer": "Error: GROQ_API_KEY is missing in the environment variables.",
            "sources": []
        }
        
    llm = ChatGroq(
        api_key=config.GROQ_API_KEY,
        model_name=config.LLM_MODEL,
        temperature=0.0
    )
    
    prompt = PromptTemplate.from_template(SYSTEM_PROMPT)
    chain = prompt | llm
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def invoke_with_retry(ctx, q):
        return chain.invoke({
            "context": ctx,
            "question": q
        })
    
    try:
        response = invoke_with_retry(context_text, clean_query)
        answer = response.content.strip()
        
        # Append dynamic footer
        current_date = date.today().strftime("%Y-%m-%d")
        answer += f"\n\nLast updated from sources: {current_date}"
        
    except Exception as e:
        print(f"[Error]: LLM invocation failed: {e}")
        answer = f"I apologize, but I encountered an error while trying to generate a response: {e}"
        
    return {
        "answer": answer,
        "sources": sources
    }

if __name__ == "__main__":
    # Test cases for the pipeline
    test_queries = [
        "What is the expense ratio of the HDFC Gold ETF?",
        "Should I invest my life savings in small cap funds?",
        "Who manages the HDFC Small Cap Fund?"
    ]
    
    for q in test_queries:
        result = generate_response(q)
        print(f"\n[Response]:\n{result['answer']}")
        if result['sources']:
            print(f"\n[Sources]:")
            for s in result['sources']:
                print(f"- {s}")
        print("\n" + "="*50)
