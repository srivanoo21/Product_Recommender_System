"""
Flask Application Entry Point
----------------------------
This script launches the main Flask web application for the product recommender system.
- Handles user queries and returns product recommendations using the RAG chain.
- Integrates with Prometheus for metrics and monitoring.
- Loads the vector store and RAG chain at startup for efficient inference.
- Provides web routes for chat UI and metrics endpoint.
"""

from flask import render_template,Flask,request,Response
from prometheus_client import Counter,generate_latest
from product.data_ingestion import DataIngestor
from product.rag_chain import RAGChainBuilder

from dotenv import load_dotenv

# Loads environment variables from a .env file for configuration (API keys, etc.).
load_dotenv()

# Sets up a Prometheus counter to track the total number of HTTP requests to the app.
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Request")

def create_app():

    app = Flask(__name__) 

    # Loads or builds the vector store (semantic search database).
    vector_store = DataIngestor().ingest(load_existing=True)
    
    # Initializes the RAG chain for conversational recommendations.
    # It builds and returns the entire RAG pipeline (the chain object), but does not run it yet.
    rag_chain = RAGChainBuilder(vector_store).build_chain()

    # Increments the request counter and Renders the main chat UI page.
    @app.route("/")
    def index():
        REQUEST_COUNT.inc()
        return render_template("index.html")
    

    # Handles POST requests from the chat UI.
    # Gets the user’s message, invokes the RAG chain, and returns the generated answer.
    @app.route("/get" , methods=["POST"])
    def get_response():

        user_input = request.form["msg"]

        # config={"configurable": {"session_id": "user-session"}} tells the chain which session ID to use for chat history management.
        # The RAG chain is wrapped with RunnableWithMessageHistory, which uses the session_id to keep track of each user's conversation history.
        # By passing a unique session_id (here, "user-session"), we ensure that the chat history is correctly associated with each user or session.
        # If we had multiple users, we would generate a different session_id for each, so their chat histories don't mix.
        reponse = rag_chain.invoke(
            {"input" : user_input},
            config={"configurable" : {"session_id" : "user-session"}}
        )["answer"]

        return reponse
    
    # Exposes a /metrics endpoint for Prometheus to scrape app metrics.
    @app.route("/metrics")
    def metrics():
        return Response(generate_latest(), mimetype="text/plain")
    
    return app


if __name__=="__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
