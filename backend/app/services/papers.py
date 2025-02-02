from llama_index.readers.papers import ArxivReader, PubmedReader
from llama_index.core import VectorStoreIndex, StorageContext
from app.config import ASTRA_DB_APPLICATION_TOKEN, ASTRA_DB_API_ENDPOINT
from llama_index.vector_stores.astra_db import AstraDBVectorStore
from llama_index.core.tools import FunctionTool
from app.services.vector_store import vector_stores, embed_model
from app.utils.logger import logger
from fastapi import HTTPException

def paper_loader(category: str):
    if category == "tech":
        loader = ArxivReader()
    elif category == "medical":
        loader = PubmedReader()
    return loader

def process_papers(category: str, paper: str, loader) -> tuple[int, VectorStoreIndex]:
    """Process PDF and add to vector store"""
    try:

        documents = loader.load_data(search_query=f"ti:{paper}")
                
        # Get vector store for category
        astra_db_store = AstraDBVectorStore(
            token=ASTRA_DB_APPLICATION_TOKEN,
            api_endpoint=ASTRA_DB_API_ENDPOINT,
            collection_name=f"{category}_collections",
            embedding_dimension=768
        )

        storage_context = StorageContext.from_defaults(vector_store=astra_db_store)
        
        # Create or update index
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            embed_model=embed_model
        )
        
        # Update cache
        vector_stores[category] = index
        
        return index
    
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")