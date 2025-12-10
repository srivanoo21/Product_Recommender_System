"""
RAG Chain Builder Script
-----------------------
This script constructs a Retrieval-Augmented Generation (RAG) chain for conversational product recommendations.
- Uses chat history to rewrite user queries for better context.
- Retrieves relevant product reviews from the vector store.
- Formats context and generates answers using an LLM (Groq).
- Integrates with Flask app for interactive Q&A and monitoring.
"""

# Imports required for RAG chain construction and chat history management
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.documents import Document
from typing import List, Dict, Any
from product.config import Config

class RAGChainBuilder:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.model = ChatGroq(model=Config.RAG_MODEL, temperature=0.5)
        self.history_store = {}
 
    def _get_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.history_store:
            self.history_store[session_id] = ChatMessageHistory()
        return self.history_store[session_id]

    def build_chain(self):
        
        # Converts the vector store into a retriever that can fetch the top 3 most relevant documents for a query.
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})

        # Rewrite prompt  -  Used to rewrite the user’s question as a standalone question, using the chat history for context.
        context_prompt = ChatPromptTemplate.from_messages([
            ("system", "Given the chat history and user question, rewrite it as a standalone question."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])

        # QA prompt - Used to generate the final answer, given the context (retrieved reviews) and the user’s question.
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", "You're an e-commerce bot answering product-related queries using reviews and titles. "
                       "Stick to context. Be concise and helpful.\n\nCONTEXT:\n{context}\n\nQUESTION: {input}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])

        # Utility: always convert LLM output to plain text
        def to_text(msg) -> str:
            return getattr(msg, "content", str(msg))

        # 1) Rewrite to STRING (not AIMessage) - Reformulates the user’s question using the context prompt and LLM, so the retriever gets a more focused query.
        def rewrite_question(inputs: Dict[str, Any]) -> str: 
            msg = (context_prompt | self.model).invoke(inputs)
            return to_text(msg)

        # 2) Retrieve docs using rewritten STRING - Uses the rewritten question to fetch the most relevant product reviews from the vector store.
        def get_relevant_documents(inputs: Dict[str, Any]) -> List[Document]:
            rq = rewrite_question(inputs)          # rq is a str now
            return retriever.invoke(rq) 

        # 3) Format docs
        def format_docs(docs: List[Document]) -> str:
            return "\n\n".join(doc.page_content for doc in docs)

        # 4) Build chain; ensure final output is {"answer": "..."}
        rag_chain = (
            RunnablePassthrough.assign(
                context=lambda x: format_docs(get_relevant_documents(x))
            )
            | qa_prompt
            | self.model
            | RunnableLambda(lambda msg: {"answer": to_text(msg)})  # <-- IMPORTANT
        )

        # Using RunnableWithMessageHistory ensures our RAG chain is stateful and conversational, so each user’s chat history is maintained and used for context-aware question rewriting and answering.
        # Below line only returns the RAG pipeline (the chain object) with all the logic and chat history management set up.
        # It does not run the chain or generate an answer until we call .invoke(...) on this object with user input.
        return RunnableWithMessageHistory(
            rag_chain,
            self._get_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
