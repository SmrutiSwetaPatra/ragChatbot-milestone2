import sys
import os

# Ensure src modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src.rag_pipeline import generate_response

# Streamlit Page Configuration
st.set_page_config(
    page_title="Mutual Fund FAQ Assistant",
    page_icon="📈",
    layout="centered"
)

# Custom Styling
st.markdown("""
<style>
    .disclaimer {
        background-color: #ffe6e6;
        color: #cc0000;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 25px;
        border: 1px solid #ffcccc;
    }
</style>
""", unsafe_allow_html=True)

# Layout & Disclaimer
st.title("📈 Mutual Fund FAQ Assistant")
st.markdown('<div class="disclaimer">⚠️ Facts-only. No investment advice. This tool only provides objective data based on official Groww sources.</div>', unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Example Queries
st.markdown("**Try asking:**")
col1, col2, col3 = st.columns(3)
if col1.button("What is the expense ratio of HDFC Small Cap?"):
    st.session_state.example_query = "What is the expense ratio of HDFC Small Cap?"
if col2.button("Who is the manager for the Mid Cap fund?"):
    st.session_state.example_query = "Who is the manager for the Mid Cap fund?"
if col3.button("Should I invest in gold right now?"):
    st.session_state.example_query = "Should I invest in gold right now?"

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input or example query button click
prompt = st.chat_input("Ask a question about mutual funds...")
if getattr(st.session_state, 'example_query', None):
    prompt = st.session_state.example_query
    st.session_state.example_query = None

if prompt:
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Searching official factsheets..."):
            result = generate_response(prompt)
            
            answer_text = result['answer']
            if result.get('sources'):
                answer_text += "\n\n**Sources:**\n"
                for s in result['sources']:
                    answer_text += f"- [{s}]({s})\n"
                    
            st.markdown(answer_text)
            
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": answer_text})
