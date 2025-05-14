from fastapi import HTTPException
from google.genai import Client, types
from app.config import GEMINI_API_KEY
from app.utils.logger import logger
from google.genai import types, Client
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from app.services.vector_store import get_vector_store, doc_llm

gemini_client = Client(api_key=GEMINI_API_KEY)
search_tool = Tool(google_search=GoogleSearch())

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
            model="gemini-2.0-flash",
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
            model="gemini-2.0-flash",
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
            model="gemini-2.0-flash", 
            config=config,
            contents=prompt
        )
        
        logger.info("Successfully searched the web with Gemini")
        return response.text
        
    except Exception as e:
        logger.error(f"Error in web search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Web Search failed: {str(e)}")

def process_query(category: str, query: str) -> str:
    """Process a query using the appropriate vector store"""
    try:
        logger.info(f"Processing query for category: {category}")
        index = get_vector_store(category)

        logger.info(f"Using vector store for category: {category}")
        query_engine = index.as_query_engine(llm=doc_llm)

        logger.info(f"Querying vector store for category: {category}")
        response = query_engine.query(query)

        logger.info(f"Successfully processed query for category: {category}")
        return str(response.response)
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
