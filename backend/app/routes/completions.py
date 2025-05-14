from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.models.completion import CompletionResponse
from app.services.file_processing import process_pdf, perform_pdf_query, cleanup_astra_collection
from app.services.handlers import analyze_audio, analyze_image, process_query, web_search
from app.services.papers import process_papers, paper_loader
from app.utils.auth import verify_api_key
from app.utils.logger import logger

router = APIRouter(prefix="/openai/v1/completions")


# Text completion Endpoint
@router.post("/text")
def text_completion(
    category: str,
    prompt: str, 
    secret: str = Depends(verify_api_key)
):
    """Handle text completion requests"""
    try:
        logger.info(f"Received text completion request for category: {category}")

        response_text = process_query(category, prompt)
        return CompletionResponse(response=response_text)
    except Exception as e:
        logger.error(f"Error in text completion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Web Search completion endpoint
@router.post("/search")
def web_search_completion(
    category: str,
    prompt: str, 
    secret: str = Depends(verify_api_key)
):
    """Handle web search requests"""
    try:
        logger.info(f"Received web search request for category: {category}")

        search_response = web_search(category, prompt)
        return CompletionResponse(response=search_response)
    except Exception as e:
        logger.error(f"Error in web search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Research Papers Endpoint
@router.post("/papers")
async def paper_completion(
    category: str,
    prompt: str,
    paper: str,
    secret: str = Depends(verify_api_key)
):
    """Handle Research Paper Search and Querying"""
    try:
        logger.info(f"Received research paper completion request for category: {category}")
        
        loader = paper_loader(category)

        # Process Papers and add to vector store
        _ = process_papers(category, paper, loader)
        
        # Query the processed content
        response_text = process_query(category, prompt)
        
        return CompletionResponse(response=response_text)
    except Exception as e:
        logger.error(f"Error in research paper completion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Audio completion endpoint
@router.post("/audio")
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


# Drop Collection
@router.get("/nuke")
async def clean_collection(secret: str = Depends(verify_api_key)):
    """Drop the pdf collection from the database"""
    try:
        logger.info(f"Initiated pdf_collections destruction")

        cleanup_astra_collection()
    except Exception as e:
        logger.error(f"Error in dropping pdf collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Document endpoint
@router.post("/pdfs")
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
        response_text = perform_pdf_query(prompt)
        
        return CompletionResponse(response=response_text)
    except Exception as e:
        logger.error(f"Error in PDF completion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Image completion endpoint
@router.post("/image")
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
