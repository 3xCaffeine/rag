from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
from pydantic import BaseModel
from enum import Enum, auto
import logging
import os
import sys

def setup_logger():
    logger = logging.getLogger('rag_logger')

    formatter = logging.Formatter('%(levelname)s - [%(asctime)s] - %(message)s', datefmt='%d/%b/%Y %H:%M:%S')

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger

logger = setup_logger()

app = FastAPI()

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

class ChatInput(BaseModel):
    message: str

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

@app.post("openai/v1/chat/completions", tags=["chat"], summary="Send user messages and game state to API")
async def chat_endpoint(
    chat_input: ChatInput,
    secret: str = Depends(verify_api_key)
):
    try:
        logger.info(f"Received chat request: {chat_input.message[:50]}...")
        logger.info(f"Completed games: {chat_input.completed_games}")
        
        response_text = await bot.get_response(
            chat_input.message,
            chat_input.completed_games
        )
        
        return ChatResponse(
            response=response_text,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")