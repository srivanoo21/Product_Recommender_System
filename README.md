# Flipkart Product Recommender System

This project is an end-to-end, production-ready, Large Language Model (LLM)-powered product recommendation system for Flipkart product reviews. It leverages Retrieval-Augmented Generation (RAG), vector databases, and modern MLOps observability tools (Prometheus, Grafana) to deliver context-aware, conversational product recommendations.

---

## Features

- **Conversational Product Recommendations:**  
  Users can ask product-related questions in natural language and receive context-rich, review-based answers.

- **RAG Pipeline:**  
  Combines a vector database (AstraDB) for semantic search with an LLM (Groq/LLM API) for answer generation.

- **LLM Embeddings:**  
  Uses HuggingFace endpoint embeddings (`BAAI/bge-base-en-v1.5`) to encode product reviews.

- **Chat History Awareness:**  
  The system rewrites user queries using chat history for more accurate, context-aware retrieval.

- **Observability:**  
  Prometheus scrapes app metrics (e.g., HTTP request count), and Grafana provides dashboards for monitoring.

- **Kubernetes-Ready:**  
  Includes deployment YAMLs for Prometheus and Grafana, with NodePort services for easy access.

---

## Architecture Overview

1. **Data Ingestion:**  
   - `flipkart/data_ingestion.py` loads product reviews from CSV, converts them to vector documents, and stores them in AstraDB.
   - Embeddings are generated using HuggingFace endpoints.

2. **RAG Chain Construction:**  
   - `flipkart/rag_chain.py` builds a chain that:
     - Rewrites user queries using chat history and a prompt template.
     - Retrieves relevant reviews from AstraDB using semantic search.
     - Formats retrieved reviews as context.
     - Passes context and the user query to the LLM for answer generation.

3. **Flask Web App:**  
   - `app.py` serves a web interface for user queries.
   - Handles user input, invokes the RAG chain, and returns answers.
   - Exposes a `/metrics` endpoint for Prometheus.

4. **Monitoring:**  
   - `prometheus/prometheus-deployment.yaml` and `prometheus/prometheus-configmap.yaml` deploy and configure Prometheus to scrape metrics from the Flask app.
   - `grafana/grafana-deployment.yaml` deploys Grafana for dashboard visualization.

---

## Key Files and Directories

- `flipkart/data_ingestion.py` — Loads and embeds product reviews into AstraDB.
- `flipkart/data_converter.py` — Converts CSV rows to LangChain `Document` objects.
- `flipkart/rag_chain.py` — Builds the RAG chain for conversational retrieval and answer generation.
- `flipkart/config.py` — Loads environment variables and model/configuration settings.
- `app.py` — Flask app entry point; handles user queries and exposes metrics.
- `data/flipkart_product_review.csv` — Source data for product reviews.
- `prometheus/` — Kubernetes YAMLs for Prometheus monitoring.
- `grafana/` — Kubernetes YAMLs for Grafana dashboards.
- `.env.example` — Template for required environment variables (do not commit secrets).

---

## Configuration

- **Environment Variables:**  
  Set in `.env` (not committed). Example:
  ```
  ASTRA_DB_API_ENDPOINT=...
  ASTRA_DB_APPLICATION_TOKEN=...
  ASTRA_DB_KEYSPACE=...
  GROQ_API_KEY=...
  ```

- **Models Used:**  
  - Embedding: `BAAI/bge-base-en-v1.5`
  - LLM: `llama-3.1-8b-instant` (via Groq API)

---

## How It Works

1. **Startup:**  
   - The app loads or builds the vector store from product reviews.
   - The RAG chain is initialized with chat history support.

2. **User Query:**  
   - User submits a question via the web UI.
   - The system rewrites the question using chat history for context.
   - Retrieves the most relevant reviews from AstraDB.
   - Passes the reviews and question to the LLM for answer generation.
   - Returns a concise, context-aware answer.

3. **Monitoring:**  
   - Prometheus scrapes `/metrics` from the Flask app.
   - Grafana visualizes metrics for observability.

---

## Deployment

- **Local:**  
  1. Install dependencies: `pip install -r requirements.txt`
  2. Set up `.env` with required keys.
  3. Run: `python app.py`
  4. Access the app at `http://localhost:5000`

- **Kubernetes:**  
  1. Apply Prometheus and Grafana YAMLs in the `prometheus/` and `grafana/` folders.
  2. Expose services via NodePort for external access.

---

## Security

- **Never commit secrets:**  
  `.env` is in `.gitignore`. Use `.env.example` for sharing variable names only.
- **API keys and tokens** must be set in your environment before running the app.

---

## Extending

- Add new data sources by updating `data/flipkart_product_review.csv`.
- Change the embedding or LLM model in `flipkart/config.py`.
- Customize prompts in `flipkart/rag_chain.py` for different conversational behaviors.

---

## Authors

- Project by srivanoo21

---

## Full Setup & Deployment Guide

For a step-by-step, hands-on guide to setting up, deploying, and monitoring this project—including Docker, Kubernetes, Minikube, Prometheus, and Grafana—see the [`FULL DOCUMENTATION.md`](./FULL%20DOCUMENTATION.md) file in this repository. It contains:
- Initial setup and prerequisites
- VM and cloud configuration
- Docker and Minikube installation
- GitHub integration
- Kubernetes deployment
- Monitoring setup with Prometheus and Grafana
- Example commands and troubleshooting tips

Follow the steps in `FULL DOCUMENTATION.md` for a smooth end-to-end deployment experience.


