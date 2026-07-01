import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import src.config as config
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from tenacity import retry, stop_after_attempt, wait_exponential

# Pre-defined polite refusal
REFUSAL_MESSAGE = "I can only provide factual information about mutual funds based on Groww's data. I cannot provide investment advice, predict future performance, or offer personalized recommendations. Please consult SEBI or AMFI resources for guidance."

# Hardcoded keyword heuristics for ultra-fast rejection
ADVISORY_KEYWORDS = [
    "should i invest", "best fund to buy", "recommend", "advice", 
    "is it a good time", "will it go up", "predict", "guarantee", 
    "which fund is better", "my portfolio", "what should i do"
]

def is_advisory_keyword_match(query: str) -> bool:
    """Fast-path check using simple heuristics."""
    q_lower = query.lower()
    for kw in ADVISORY_KEYWORDS:
        if kw in q_lower:
            return True
    return False

def evaluate_query(query: str) -> bool:
    """
    Evaluates whether a query is factual (True) or advisory/subjective (False).
    Returns True if the query is safe to process, False otherwise.
    """
    # 1. Fast-path check
    if is_advisory_keyword_match(query):
        return False
        
    # 2. LLM-based classification
    if not config.GROQ_API_KEY:
        print("Warning: GROQ_API_KEY not set. Falling back to keyword check only.")
        return True
        
    llm = ChatGroq(
        api_key=config.GROQ_API_KEY,
        model_name=config.LLM_MODEL,
        temperature=0.0
    )
    
    prompt = PromptTemplate.from_template(
        """You are a strict guardrail classifier for a Mutual Fund FAQ assistant. 
        Your job is to classify the user's query into one of two categories: 'FACTUAL' or 'ADVISORY'.
        
        - 'FACTUAL': The query asks for objective data, definitions, past performance numbers, fund managers, expense ratios, NAV, etc.
        - 'ADVISORY': The query asks for subjective opinions, investment advice, future predictions, recommendations, or personalized portfolio reviews.
        
        Reply ONLY with the exact word 'FACTUAL' or 'ADVISORY'. Do not provide any other text.
        
        Query: "{query}"
        Classification:"""
    )
    
    chain = prompt | llm
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def invoke_with_retry(q):
        return chain.invoke({"query": q})
        
    try:
        response = invoke_with_retry(query)
        classification = response.content.strip().upper()
        
        if classification == "ADVISORY":
            return False
        return True
    except Exception as e:
        print(f"Error during LLM classification: {e}")
        # Fail open if the LLM is down, rely on the RAG prompt's built-in constraints later.
        return True

def process_query_input(query: str) -> dict:
    """
    Main entry point for Phase 3. 
    Cleans the query and runs guardrails.
    Returns a dictionary with status and processed query.
    """
    # 1. Input pre-processing
    clean_query = query.strip()
    
    # 2. Guardrail check
    is_safe = evaluate_query(clean_query)
    
    if not is_safe:
        return {
            "is_safe": False,
            "response": REFUSAL_MESSAGE
        }
        
    return {
        "is_safe": True,
        "query": clean_query
    }

if __name__ == "__main__":
    # Test cases
    test_queries = [
        "What is the NAV of HDFC Gold ETF?",
        "Should I invest my life savings in small cap funds?",
        "Who is the fund manager for the Mid Cap fund?",
        "Is it a good time to buy silver right now?"
    ]
    
    print("Testing Guardrails...\n")
    for q in test_queries:
        print(f"Query: '{q}'")
        res = process_query_input(q)
        if res["is_safe"]:
            print("Status: ALLOWED (Factual)\n")
        else:
            print(f"Status: BLOCKED (Advisory)\nResponse: {res['response']}\n")
