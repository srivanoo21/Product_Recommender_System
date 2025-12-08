"""
Data Converter Script
---------------------
This script reads product review data from a CSV file and converts each row into a LangChain Document object.
- Extracts 'product_title' and 'review' columns from the CSV.
- Creates Document objects with review text as content and product title as metadata.
- Used for preparing data for ingestion into the vector store for semantic search and retrieval.
"""

import pandas as pd
from langchain_core.documents import Document

class DataConverter:
    def __init__(self,file_path:str):
        self.file_path = file_path

    def convert(self):
        df = pd.read_csv(self.file_path)[["product_title", "review"]]   

        docs = [
            Document(page_content=row['review'] , metadata = {"product_name" : row["product_title"]})
            for _, row in df.iterrows()
        ]

        return docs
