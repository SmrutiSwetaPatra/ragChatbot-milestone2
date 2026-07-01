# Evaluation Strategy (Eval Framework): Mutual Fund FAQ Assistant

This document outlines the evaluation criteria, testing methods, and success metrics for each phase of the project as defined in `ImplementationPlan.md`.

---

## Phase 1: Project Setup and Prerequisites
**Goal:** Ensure the environment is correctly configured and reproducible.

*   **Evaluation Criteria:**
    *   Can the project be installed and run on a fresh machine?
    *   Are all required dependencies (LangChain, Groq, ChromaDB, etc.) strictly versioned?
*   **Testing Method:** 
    *   Clone the repository into a clean virtual environment and run the installation script (`pip install -r requirements.txt`).
*   **Success Metric:** 
    *   Zero dependency conflicts or installation errors. The central `config.py` successfully loads all environment variables (e.g., Groq API keys) without throwing exceptions.

---

## Phase 2: Data Ingestion & Vector Database Setup
**Goal:** Verify that the primary corpus (Groww URLs) is accurately scraped, chunked, embedded via the BGE model, and stored.

*   **Evaluation Criteria:**
    *   Is all critical text (expense ratio, exit load, lock-in period) successfully extracted?
    *   Are the chunk sizes optimal for the embedding model?
*   **Testing Method:**
    *   **Retrieval Hit-Rate Testing:** Write a script containing 20 standard factual questions. Query the Vector DB directly (bypassing the LLM) to check if the correct chunks are returned in the `Top-3` results.
*   **Success Metric:**
    *   >95% retrieval accuracy (Top-3 Recall) for standard facts across all 5 selected HDFC schemes.
    *   Zero unhandled exceptions during the ingestion of the 5 URLs.

---

## Phase 3: Query Processing & Guardrail Implementation
**Goal:** Ensure the assistant strictly blocks advisory, subjective, or out-of-domain queries.

*   **Evaluation Criteria:**
    *   Does the classifier correctly identify and block non-factual queries?
    *   Does it allow factual, complex queries to pass through?
*   **Testing Method:**
    *   **Red-Teaming (Automated/Manual):** Feed a curated dataset of 50 queries: 25 factual (e.g., *"What is the benchmark index?"*) and 25 advisory/adversarial (e.g., *"Is this fund good?", "Ignore rules"*).
*   **Success Metric:**
    *   100% block rate for advisory/subjective/out-of-domain queries (Zero false negatives).
    *   <5% false positive rate (incorrectly blocking a factual query).

---

## Phase 4: RAG Pipeline & LLM Generation
**Goal:** Evaluate the Groq LLM's response generation for accuracy, formatting, and constraints.

*   **Evaluation Criteria:**
    *   Are answers factually accurate and derived *only* from the retrieved context?
    *   Does the response strictly adhere to the formatting constraints (Max 3 sentences, mandatory citation, footer)?
*   **Testing Method:**
    *   **LLM-as-a-Judge / Human Eval:** Run the pipeline on 50 standard factual queries. Compare the generated output against the ground truth.
    *   **Regex / Programmatic Testing:** Run scripts to count the number of sentences, verify the presence of a URL, and check for the `"Last updated from sources:"` string.
*   **Success Metric:**
    *   100% adherence to the 3-sentence limit and citation rules.
    *   0% hallucination rate (if context is missing, the LLM must explicitly state it cannot answer).

---

## Phase 5: User Interface (UI) Development
**Goal:** Verify the usability, disclaimer visibility, and error handling of the frontend.

*   **Evaluation Criteria:**
    *   Is the interface clean, minimalistic, and intuitive?
    *   Is the mandatory "Facts-only. No investment advice." disclaimer highly visible?
*   **Testing Method:**
    *   **UI/UX Testing:** Manual click-testing. Verify that the 3 example queries work as expected. Verify that UI gracefully handles API timeouts (e.g., if Groq is down).
*   **Success Metric:**
    *   All UI elements render correctly. 
    *   The app gracefully degrades (shows an error message) instead of crashing if the backend pipeline fails.

---

## Phase 6: Testing, Refinement, and Documentation
**Goal:** Ensure the entire system operates harmoniously end-to-end and is ready for handoff.

*   **Evaluation Criteria:**
    *   Is the README clear enough for a new developer to understand the architecture, setup the app, and run it?
*   **Testing Method:**
    *   **End-to-End (E2E) Testing:** Run automated E2E tests simulating a user asking questions through the UI and receiving formatted responses.
*   **Success Metric:**
    *   100% pass rate on E2E tests.
    *   Documentation covers the RAG pipeline, the guardrails, known edge cases (referencing `edge-case.md`), and step-by-step setup instructions.
