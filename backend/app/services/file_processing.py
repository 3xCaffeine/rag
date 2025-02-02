import datetime
from astrapy import DataAPIClient
import hashlib
from pathlib import Path
from fastapi import HTTPException
from llama_index.vector_stores.astra_db import AstraDBVectorStore
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from app.utils.logger import logger
from app.config import PDF_STORAGE_DIR, ASTRA_DB_APPLICATION_TOKEN, ASTRA_DB_API_ENDPOINT
from app.services.vector_store import vector_stores, embed_model, get_vector_store, chat_memory, doc_llm
from llama_index.core.llms import ChatMessage, MessageRole


def save_pdf_file(file_data: bytes, category: str) -> str:
    """
    Save PDF file to local storage with a unique name
    Returns the path to the saved file
    """
    try:
        # Create category subdirectory if it doesn't exist
        category_dir = Path(PDF_STORAGE_DIR) / category
        category_dir.mkdir(exist_ok=True)

        # Generate unique filename using timestamp and content hash
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.md5(file_data).hexdigest()[:8]
        filename = f"{timestamp}_{content_hash}.pdf"
        
        # Save file
        file_path = category_dir / filename
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        logger.info(f"Saved PDF file: {file_path}")
        return str(file_path)
    
    except Exception as e:
        logger.error(f"Error saving PDF file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save PDF file: {str(e)}")

def cleanup_astra_collection() -> None:
    """Clear the contents of an AstraDB collection"""
    try:
        client = DataAPIClient(ASTRA_DB_APPLICATION_TOKEN)
        db = client.get_database(ASTRA_DB_API_ENDPOINT)

        pdfs = db.get_collection("pdf_collections")
        pdfs.drop()
        
        logger.info(f"Successfully cleared collection")
        
    except Exception as e:
        logger.error(f"Error clearing collection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Collection cleanup failed: {str(e)}")

def process_pdf(pdf_data: bytes, category: str) -> tuple[int, VectorStoreIndex]:
    """Process PDF and add to vector store"""
    try:
        # Read PDF
        pdf_path = save_pdf_file(pdf_data, category)
        
        # Read PDF using SimpleDirectoryReader
        documents = SimpleDirectoryReader(input_files=[pdf_path]).load_data()
                
        # Get vector store for category
        astra_db_store = AstraDBVectorStore(
            token=ASTRA_DB_APPLICATION_TOKEN,
            api_endpoint=ASTRA_DB_API_ENDPOINT,
            collection_name=f"pdf_collections",
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

def perform_pdf_query(query: str) -> str:
    """Process a query using the appropriate vector store"""
    try:
        index = get_vector_store("pdf")

        chat_history = chat_memory.get()
        
        chat_memory.put(ChatMessage(role=MessageRole.USER, content=query))

        query_engine = index.as_query_engine(llm=doc_llm)

        full_query = "\n".join([msg.content for msg in chat_history]) + "\n" + query
        
        response = query_engine.query(full_query)

        chat_memory.put(ChatMessage(role=MessageRole.ASSISTANT, content=response.response))

        logger.info(f"Successfully processed query for PDF")
        return str(response.response)
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))