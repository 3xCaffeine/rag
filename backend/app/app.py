from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.routes import completions

load_dotenv()

def create_app() -> FastAPI:
    app = FastAPI(title="RAGnarok API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["health"], summary="Check API health status")
    async def health():
        return {"status": "healthy"}
    
    app.include_router(completions.router)

    return app