from llama_index.vector_stores.astra_db import AstraDBVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.llms.groq import Groq
from app.config import ASTRA_DB_APPLICATION_TOKEN, ASTRA_DB_API_ENDPOINT, OLLAMA_BASE_URL, GROQ_API_KEY
from llama_index.core.memory import ChatMemoryBuffer

# Initialize chat memory (adjust token limit as needed)
chat_memory = ChatMemoryBuffer(token_limit=8000)

vector_stores = {}

embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url=OLLAMA_BASE_URL
)

doc_llm = Groq(model="deepseek-r1-distill-llama-70b", api_key=GROQ_API_KEY)

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
