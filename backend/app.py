from fastapi import FastAPI, HTTPException, Depends, Security, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
from pydantic import BaseModel
import logging
import os
import sys
import datetime
import hashlib
import uvicorn
from pathlib import Path
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
)
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.astra_db import AstraDBVectorStore
from llama_index.llms.groq import Groq
from llama_index.vector_stores.astra_db import AstraDBVectorStore
from llama_index.core import VectorStoreIndex, StorageContext
from google.genai import types, Client
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

def setup_logger():
    logger = logging.getLogger('rag_logger')

    formatter = logging.Formatter('%(levelname)s - [%(asctime)s] - %(message)s', datefmt='%d/%b/%Y %H:%M:%S')

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger

logger = setup_logger()

app = FastAPI(title="RAGnarok API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

key = APIKeyHeader(name="X-API-Key")

API_KEY = os.getenv("API_KEY")
ASTRA_DB_APPLICATION_TOKEN = os.environ.get("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_API_ENDPOINT = os.environ.get("ASTRA_DB_API_ENDPOINT")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL")

PDF_STORAGE_DIR = "data/pdfs"

doc_llm = Groq(model="deepseek-r1-distill-llama-70b", api_key=GROQ_API_KEY)
gemini_client = Client(api_key=GEMINI_API_KEY)
embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url=OLLAMA_BASE_URL
)

search_tool = Tool(google_search=GoogleSearch())

vector_stores = {}

class CompletionRequest(BaseModel):
    category: str
    prompt: str

class CompletionResponse(BaseModel):
    response: str

def get_vector_store(category: str) -> VectorStoreIndex:
    """Get or create vector store for a category"""
    if category not in vector_stores:
        astra_db_store = AstraDBVectorStore(
            token=ASTRA_DB_APPLICATION_TOKEN,
            api_endpoint=ASTRA_DB_API_ENDPOINT,
            collection_name=f"{category}_collections",
            embedding_dimension=768
        )

        vector_stores[category] = VectorStoreIndex.from_vector_store(
            vector_store=astra_db_store,
            embed_model=embed_model
        )
    return vector_stores[category]

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

def process_query(category: str, query: str) -> str:
    """Process a query using the appropriate vector store"""
    try:
        index = get_vector_store(category)
        query_engine = index.as_query_engine(llm=doc_llm)
        response = query_engine.query(query)
        logger.info(f"Successfully processed query for category: {category}")
        return str(response.response)
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def analyze_audio(audio_data: bytes, category: str) -> str:
    """
    Analyze audio using Gemini's multimodal capabilities
    """
    try:
        logger.info(f"Processing audio for category: {category}")
                
        # Create prompt for Gemini
        gemini_prompt = f"""
        Task: Analyze this audio and provide a detailed and accurate transcription.
        Context: This is for the category: {category}
        Please provide a comprehensive response.
        """
        
        # Call Gemini API with audio
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[
                gemini_prompt,
                types.Part.from_bytes(
                data=audio_data,
                mime_type="audio/mpeg"
                )
            ]
        )
        
        logger.info("Successfully processed audio with Gemini")
        return response.text
        
    except Exception as e:
        logger.error(f"Error in audio analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Audio analysis failed: {str(e)}")

def analyze_image(image_data: bytes, category: str, prompt: str) -> str:
    """
    Analyze image using Gemini's multimodal capabilities
    """
    try:
        logger.info(f"Processing image for category: {category}")
        
        # Create prompt for Gemini
        gemini_prompt = f"""
        Task: Analyze this image and provide a detailed description.
        Context: This is for the category: {category}
        User's prompt: {prompt}
        Please provide a comprehensive response.
        """
        
        # Call Gemini API with image
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[
                gemini_prompt,
                types.Part.from_bytes(
                data=image_data,
                mime_type="image/jpeg"
                )
            ]
        )
        
        logger.info("Successfully processed image with Gemini")
        return response.text
        
    except Exception as e:
        logger.error(f"Error in image analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

def web_search(category: str, prompt: str) -> str:
    """
    Perform Web Search using Gemini's multimodal capabilities
    """
    try:
        logger.info(f"Performing web search for category: {category}")
        
        config = GenerateContentConfig(
            system_instruction=(f"""
                You are a helpful assistant that provides up to date information
                to help the user in their research in the field of {category}
                """
            ),
            tools=[search_tool],
            response_modalities=["TEXT"],
            candidate_count=1
        )
        
        # Call Gemini API with to perform web search with Google Search Engine
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp", 
            config=config,
            contents=prompt
        )
        
        logger.info("Successfully searched the web with Gemini")
        return response.text
        
    except Exception as e:
        logger.error(f"Error in web search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Web Search failed: {str(e)}")

# Security
async def verify_api_key(secret: str = Security(key)):
    if secret != API_KEY:
        logger.warning(f"Invalid API key")
        raise HTTPException(status_code=401, detail="Invalid API key")
    return secret

# Routes
@app.get("/health", tags=["health"], summary="Check API health status")
async def health_check():
    return {"status": "healthy"}  

# Text completion endpoint
@app.post("/openai/v1/completions/text")
def text_completion(
    category: str,
    prompt: str, 
    secret: str = Depends(verify_api_key)
):
    """Handle text completion requests"""
    try:
        response_text = process_query(category, prompt)
        return CompletionResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Text Web Search completion endpoint
@app.post("/openai/v1/completions/search")
def web_search_completion(
    category: str,
    prompt: str, 
    secret: str = Depends(verify_api_key)
):
    """Handle web search requests"""
    try:
        search_response = web_search(category, prompt)
        return CompletionResponse(response=search_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Audio completion endpoint
@app.post("/openai/v1/completions/audio")
async def audio_completion(
    category: str,
    file: UploadFile = File(...),
    secret: str = Depends(verify_api_key)
):
    """Handle audio completion requests"""
    try:
        logger.info(f"Received audio completion request for category: {category}")
        
        # Read audio file
        audio_bytes = await file.read()
        
        # Get transcription and analysis from Gemini
        audio_analysis = analyze_audio(audio_bytes, category)
        
        # Combine audio analysis with prompt
        combined_prompt = f"User Prompt: {audio_analysis}"
        
        # Process through RAG system
        response_text = process_query(category, combined_prompt)
        return CompletionResponse(response=response_text)
    except Exception as e:
        logger.error(f"Error in audio completion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Document endpoint
@app.post("/openai/v1/completions/pdfs")
async def pdf_completion(
    category: str,
    prompt: str,
    file: UploadFile = File(...),
    secret: str = Depends(verify_api_key)
):
    """Handle PDF upload, processing, and querying"""
    try:
        logger.info(f"Received PDF completion request for category: {category}")

        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Read PDF file
        pdf_bytes = await file.read()
        
        # Process PDF and add to vector store
        _ = process_pdf(pdf_bytes, category)
        
        # Query the processed content
        response_text = process_query(category, prompt)
        
        return CompletionResponse(response=response_text)
    except Exception as e:
        logger.error(f"Error in PDF completion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Image completion endpoint
@app.post("/openai/v1/completions/image")
async def image_completion(
    category: str,
    prompt: str,
    file: UploadFile = File(...),
    secret: str = Depends(verify_api_key)
):
    """Handle image completion requests"""
    try:
        logger.info(f"Received image completion request for category: {category}")
        
        # Read image file
        image_bytes = await file.read()
        
        # Get description and analysis from Gemini
        image_analysis = analyze_image(image_bytes, category, prompt)
        
        # Combine image analysis with prompt
        combined_prompt = f"Image description: {image_analysis}\nUser prompt: {prompt}"
        
        # Process through RAG system
        response_text = process_query(category, combined_prompt)
        return CompletionResponse(response=response_text)
    except Exception as e:
        logger.error(f"Error in image completion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
