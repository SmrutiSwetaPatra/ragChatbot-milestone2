# Phase-Wise Implementation Plan: Mutual Fund FAQ Assistant

This document outlines the step-by-step implementation strategy for the Mutual Fund FAQ Assistant based on the `Architecture.md`. 

---

## Phase 1: Project Setup and Prerequisites
**Goal:** Establish the foundational codebase, repository structure, and external dependencies.

1. **Initialize Project Repository:**
   - Setup a Python virtual environment (`venv` or `conda`).
   - Create the standard directory structure (`src`, `docs`, `data`, `notebooks`).
2. **Install Dependencies:**
   - Install core libraries: `langchain`, `llama-index` (if chosen), `streamlit` (or `gradio`), `chromadb`, and relevant LLM SDKs (`groq`).
   - Setup environment variables for API keys (`.env` file).
3. **Define Configuration:**
   - Create a central configuration file (`config.py` or `config.yaml`) to hold LLM models, vector database paths, chunk sizes, and the target scheme URLs.

---

## Phase 2: Data Ingestion & Vector Database Setup
**Goal:** Scrape the provided Groww URLs, chunk the content, and store it in a Vector DB for retrieval.

1. **Document Scraping & Content Cleaning:**
   - Implement web scrapers (using `BeautifulSoup` or LangChain's `WebBaseLoader`) configured to parse only the main body content of the Groww URLs.
   - Strip out irrelevant boilerplate (navigation menus, footer links, generic stock market text) to ensure the LLM receives only mutual fund-specific facts.
   - Note: Skipping extraction from supplementary official documents (PDFs) as per explicit constraint.
2. **Optimized Text Chunking:**
   - Implement an advanced chunking strategy (e.g., `RecursiveCharacterTextSplitter` with increased chunk sizes like 1500-2000 characters and 200 character overlap) to prevent breaking up tabular data or related financial stats.
   - Ensure chunks end on logical boundaries (paragraphs or sentences) rather than splitting mid-sentence.
   - Attach metadata to each chunk (e.g., `source_url`, `scheme_name`).
3. **Vector Database Ingestion & Embedding Strategy:**
   - Initialize the Embedding model using `BAAI/bge-small-en-v1.5`. Since we have 75 highly-focused chunks, the small model (384 dimensions) provides excellent semantic accuracy without the massive memory overhead of the large model.
   - Ensure embeddings are normalized (`normalize_embeddings=True`) as recommended by BGE for accurate cosine similarity.
   - Setup the Vector Database (`ChromaDB`) configured to persist locally in the `data/chroma_db` directory.
4. **Validation:**
   - Write a quick test script to query the Vector DB directly to ensure relevant chunks are successfully retrieved.

---

## Phase 3: Query Processing & Guardrail Implementation
**Goal:** Intercept user queries and ensure only factual mutual fund questions are processed.

1. **Input Pre-processing:**
   - Clean the user's raw input query.
2. **Guardrail / Classifier Setup:**
   - Implement a lightweight classifier (either rule-based keywords or a fast LLM call) to classify the intent of the prompt: `factual` vs. `advisory/subjective`.
3. **Refusal Mechanism:**
   - Create a polite, pre-defined fallback response for `advisory` queries.
   - Example: *"I can only provide factual information about mutual funds. I cannot provide investment advice or recommendations. Please consult SEBI or AMFI resources for guidance."*

---

## Phase 4: RAG Pipeline & LLM Generation
**Goal:** Retrieve context from the Vector DB and generate constrained, factual responses.

1. **Retrieval Mechanism:**
   - Take the `factual` user query, convert it into an embedding, and perform a similarity search (`Top-K = 3 or 5`) against the Vector DB.
2. **Prompt Engineering:**
   - Construct a strict `System Prompt` that enforces constraints:
     - Answer only based on provided context.
     - Maximum 3 sentences.
     - Cite the exact source URL.
3. **LLM Integration:**
   - Pass the system prompt, retrieved chunks (with metadata), and user query to the primary LLM via Groq (e.g., `llama3-70b-8192`).
4. **Rate Limit & Token Management:**
   - Handle Groq's `llama-3.3-70b-versatile` strict tier limits (30 Requests Per Minute, 12K Tokens Per Minute).
   - Implement exponential backoff (e.g. using `tenacity`) for LLM calls to gracefully catch and retry `RateLimitError`.
   - Ensure retrieved context is concise to respect the 12K TPM limit.
5. **Output Formatting:**
   - Parse the LLM output to verify sentence constraints.
   - Append the mandatory footer dynamically: `Last updated from sources: <current_date>`.

---

## Phase 5: User Interface (UI) Development
**Goal:** Build a minimal, clean interface for end users to interact with the assistant.

1. **UI Framework Setup:**
   - Initialize a Streamlit or Gradio application.
2. **Layout & Disclaimer:**
   - Add a welcome message and a static, highly visible disclaimer: **"Facts-only. No investment advice."**
3. **Example Queries:**
   - Add 3 clickable example query buttons (e.g., *"What is the expense ratio of HDFC Small Cap Fund?"*).
4. **Chat Interface Integration:**
   - Connect the chat UI to the Phase 4 RAG pipeline, handling loading states and displaying the response with the citation and footer.

---

## Phase 6: Scheduler Component
**Goal:** Automate the data ingestion process to run daily so that the latest mutual fund data is always available in the Vector DB.

1. **GitHub Actions Setup:**
   - Create a GitHub Actions workflow (e.g., `.github/workflows/daily_ingestion.yml`) triggered by a `schedule` event using cron syntax.
2. **Ingestion Trigger:**
   - Configure the workflow to set up the Python environment, install dependencies, and run the main ingestion script built in Phase 2.
3. **Execution & Logging:**
   - Handle the persistence of the updated Vector DB appropriately (e.g., committing changes back to the repository or uploading them to cloud storage).
   - Utilize GitHub Actions run logs to monitor the success, failure, and timestamp of the daily data ingestion runs.

---

## Phase 7: Testing, Refinement, and Documentation
**Goal:** Ensure the system strictly adheres to the problem statement constraints and is ready for use.

1. **Constraint Testing (Red Teaming):**
   - Test with aggressive advisory questions to ensure the guardrails hold.
   - Test with performance comparison questions to ensure it only provides links to factsheets.
2. **Accuracy Testing:**
   - Verify that retrieved factual data (expense ratios, exit loads) perfectly matches the official Groww source URLs.
3. **Documentation:**
   - Update the `README.md` with:
     - Setup & Installation instructions.
     - Architecture overview.
     - Known limitations.
4. **Final Review:**
   - End-to-end walkthrough to verify the 3-sentence limit, correct citations, and date footers are consistently applied.
