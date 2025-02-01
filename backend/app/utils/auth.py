from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from app.config import API_KEY
from app.utils.logger import logger

key = APIKeyHeader(name="X-API-Key")

async def verify_api_key(secret: str = Security(key)):
    if secret != API_KEY:
        logger.warning("Invalid API key")
        raise HTTPException(status_code=401, detail="Invalid API key")
    return secret