# Explanation of Role 4 Tasks in CP0 (RAG & Agent)

This document provides a technical explanation of the tasks required for Role 4 in Checkpoint 0, along with an analysis of the corresponding code.

---

## 1. Understanding `LocalEmbeddingIndex`, `embeddings`, and `agent`

### a. `embeddings.py` (Embedding Model)
- **What it does:** This file configures the embedding model used to convert text into vector representations.
- **Input/Output:**
  - `embed_documents(texts)`: Takes a list of strings (e.g., the `text_for_embedding` from each paper) and returns a matrix of embedding vectors to be stored in the database.
  - `embed_query(text)`: Takes a user query string and converts it into a single vector for similarity comparison.
- **Significance:** This is the core component that bridges natural language and mathematical representations. Recently, we updated this to use `langchain_openai.OpenAIEmbeddings` (specifically `text-embedding-3-small`) to leverage high-quality OpenAI embeddings instead of the local MiniLM model.

### b. `index.py` (`LocalEmbeddingIndex` - Vector Database)
- **What it does:** Manages the lifecycle of ChromaDB (creating, storing, and searching data).
- **Build Process (Input/Output):**
  - **Input:** The `build()` method receives a `pd.DataFrame` containing the cleaned data.
  - **Process:** It iterates through the DataFrame, processes the `text_for_embedding` and extracts `metadata`. It then pushes everything into ChromaDB.
  - **Output:** Returns a `LocalEmbeddingIndex` instance and saves a `manifest.json` file to track the database configuration.
- **Search & Lookup:**
  - `search(query, top_k)`: Uses the query's vector to find the top `k` most similar documents in ChromaDB. Returns a list of `SearchResult` objects.
  - `lookup(value)`: Finds an exact paper match based on ID or Title using pre-loaded in-memory dictionaries (`documents_by_paper_id` and `documents_by_title`).

### c. `agent.py` (LLM Agent)
- **What it does:** Creates an intelligent Agent using LangChain.
- **Input/Output:**
  - It provides the LLM with two tools: `semantic_search_papers` (which calls the index's `search` method) and `lookup_paper` (which calls `lookup`).
  - The LLM decides which tool to use based on the user's question, and the tool's result becomes the input for the LLM to synthesize the final answer.
- **Significance:** The System Prompt explicitly instructs the LLM: *"Use tools before answering factual questions"*. This strictly grounds the LLM to the database and prevents hallucinations.

---

## 2. Finalizing the Embedding Model, Collection Naming, and Metadata

- **Embedding Model:** We have configured the system to use OpenAI's `text-embedding-3-small` via the `EMBEDDING_MODEL` environment variable. This provides superior semantic search capabilities using a 1536-dimensional vector space.
- **Collection Naming:**
  In the `_derive_collection_name` method, the system uses flexible naming:
  - Clean baseline data: `papers-baseline`
  - Corrupted data: `papers-corrupted`
  - Repaired data: `papers-repaired`
  - *Significance:* Separating collection names allows us to store all three database versions for comparison in CP6 without overwriting them.
- **Minimum Metadata:** The code extracts `paper_id`, `title`, `published`, `authors_joined`, `categories_joined`, and `summary`.
  - *Significance:* This metadata is mandatory because the evaluation system (`qa.py`) uses strict Python code to extract information from the metadata (e.g., when asked "who authored...", it directly checks the `authors_joined` field against the Ground Truth).

---

## 3. Preparing Smoke Queries/Lookups

Based on the `_extract_answer` function in `qa.py`, we prepare the following sample queries (smoke queries) to run after indexing:
- **Summary Question:** `What is the summary of '{title}'?`
- **Authors Question:** `Who authored '{title}'?`
- **Date Question:** `When was '{title}' published?`
- **Categories Question:** `What categories does '{title}' belong to?`

*Significance:* These are "primer" questions for testing. If the database returns the correct results for these, it proves that the pipeline from Raw -> Clean -> Embeddings is functioning correctly and is ready for automated Evaluation.
