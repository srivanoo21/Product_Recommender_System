# Flipkart Product Recommender System

This project is an end-to-end, production-ready, Large Language Model (LLM)-powered product recommendation system for Flipkart product reviews. It leverages Retrieval-Augmented Generation (RAG), vector databases, and modern MLOps observability tools (Prometheus, Grafana) to deliver context-aware, conversational product recommendations.

---

## Quick Start: VM, Deployment & Monitoring

This section summarizes the essential hands-on steps for setting up a VM, deploying the app, and enabling monitoring with Prometheus and Grafana. For full details, see [`FULL DOCUMENTATION.md`](./FULL%20DOCUMENTATION.md).

### 1. Create a VM (e.g., Google Cloud)
- Choose Ubuntu 24.04 LTS, 16GB RAM, 256GB disk, enable HTTP/HTTPS traffic.
- SSH into your VM.

### 2. Clone Your Repo
```bash
git clone https://github.com/srivanoo21/Product_Recommender_System.git
cd Product_Recommender_System
```

### 3. Install Docker
- Follow the official Docker docs for Ubuntu (install, post-install steps, enable on boot).
- Test with: `docker run hello-world`

### 4. Install Minikube & kubectl
- Follow official Minikube docs for Linux (binary download).
- Start Minikube: `minikube start`
- Install kubectl (e.g., `sudo snap install kubectl --classic`)
- Check: `minikube status`, `kubectl get nodes`

### 5. Build & Deploy the App
```bash
eval $(minikube docker-env)
docker build -t flask-app:latest .
kubectl create secret generic llmops-secrets \
  --from-literal=GROQ_API_KEY="" \
  --from-literal=ASTRA_DB_APPLICATION_TOKEN="" \
  --from-literal=ASTRA_DB_KEYSPACE="default_keyspace" \
  --from-literal=ASTRA_DB_API_ENDPOINT="" \
  --from-literal=HF_TOKEN="" \
  --from-literal=HUGGINGFACEHUB_API_TOKEN=""
kubectl apply -f flask-deployment.yaml
kubectl get pods
kubectl port-forward svc/flask-service 5000:80 --address 0.0.0.0
# Access your app at http://<VM_EXTERNAL_IP>:5000
```

### 6. Prometheus & Grafana Monitoring
```bash
kubectl create namespace monitoring
kubectl apply -f prometheus/prometheus-configmap.yaml
kubectl apply -f prometheus/prometheus-deployment.yaml
kubectl apply -f grafana/grafana-deployment.yaml
kubectl port-forward --address 0.0.0.0 svc/prometheus-service -n monitoring 9090:9090
# Prometheus: http://<VM_EXTERNAL_IP>:9090 (default admin:admin)
kubectl port-forward --address 0.0.0.0 svc/grafana-service -n monitoring 3000:3000
# Grafana: http://<VM_EXTERNAL_IP>:3000 (default admin:admin)
```

**Important:**
- In `prometheus/prometheus-configmap.yaml`, set the `targets` field for the Flask app to your VM's external IP and port (e.g., `['<VM_EXTERNAL_IP>:5000']`).
- Configure Grafana: Add Prometheus as a data source at `http://prometheus-service.monitoring.svc.cluster.local:9090`.

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
  1. Follow the **Quick Start: VM, Deployment & Monitoring** steps above for a practical, hands-on setup.
  2. For detailed instructions, see [`FULL DOCUMENTATION.md`](./FULL%20DOCUMENTATION.md).

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

## Monitoring: Prometheus & Grafana

**Prometheus** is an open-source monitoring and alerting toolkit designed for reliability and scalability. It collects metrics from your application (such as HTTP request counts, latency, resource usage, etc.) at regular intervals and stores them in a time-series database. Prometheus can also trigger alerts based on metric thresholds.

**Grafana** is an open-source analytics and visualization platform. It connects to Prometheus (and other data sources) to create interactive dashboards, charts, and graphs for real-time monitoring and historical analysis.

**Why do we need them?**
- They provide deep visibility into your application's health, performance, and usage.
- You can track metrics, detect anomalies, and troubleshoot issues quickly.
- They enable proactive alerting and capacity planning.
- In production, monitoring is essential for reliability, debugging, and scaling.

**In this project:**
- Prometheus scrapes metrics from the Flask app (via `/metrics` endpoint).
- Grafana visualizes these metrics, allowing you to monitor the recommender system in real time.
- Both are deployed via Kubernetes manifests (`prometheus/` and `grafana/` folders).

**See the Quick Start section above for hands-on setup steps.**

See the [`FULL DOCUMENTATION.md`](./FULL%20DOCUMENTATION.md) for setup and usage instructions.

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


