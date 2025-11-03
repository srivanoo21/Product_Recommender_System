# flipkart/rag_chain.py
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.documents import Document
from typing import List, Dict, Any
from flipkart.config import Config

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
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})

        # ---- Rewrite prompt
        context_prompt = ChatPromptTemplate.from_messages([
            ("system", "Given the chat history and user question, rewrite it as a standalone question."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])

        # ---- QA prompt
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", "You're an e-commerce bot answering product-related queries using reviews and titles. "
                       "Stick to context. Be concise and helpful.\n\nCONTEXT:\n{context}\n\nQUESTION: {input}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])

        # Utility: always convert LLM output to plain text
        def to_text(msg) -> str:
            return getattr(msg, "content", str(msg))

        # 1) Rewrite to STRING (not AIMessage)
        def rewrite_question(inputs: Dict[str, Any]) -> str:
            msg = (context_prompt | self.model).invoke(inputs)
            return to_text(msg)

        # 2) Retrieve docs using rewritten STRING
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

        return RunnableWithMessageHistory(
            rag_chain,
            self._get_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
