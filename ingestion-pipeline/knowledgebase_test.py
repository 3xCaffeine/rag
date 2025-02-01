from llama_index.core import VectorStoreIndex
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.astra_db import AstraDBVectorStore
import os
from dotenv import load_dotenv
from llama_index.llms.groq import Groq

load_dotenv()

embed_model = OllamaEmbedding(model_name="nomic-embed-text")
astra_api_endpoint = os.getenv("ASTRA_DB_ENDPOINT")
astra_db_token = os.getenv("ASTRA_DB_TOKEN")
groq_api_token = os.getenv("GROQ_API_TOKEN")


def get_vector_store():
    """Get vector store for a category"""

    astra_db_store = AstraDBVectorStore(
        token=astra_db_token,
        api_endpoint=astra_api_endpoint,
        collection_name="medical_collections",
        embedding_dimension=768,
    )
    index = VectorStoreIndex.from_vector_store(
        vector_store=astra_db_store, embed_model=embed_model
    )
    llm = Groq(model="deepseek-r1-distill-llama-70b", api_key=groq_api_token)
    query_engine = index.as_query_engine(streaming=True, llm=llm, similarity_top_k=1)
    response = query_engine.query("A BRIEF REVIEW OF THE VERTEBRAL COLUMN")
    return str(response.print_response_stream())


if __name__ == "__main__":
    result = get_vector_store()
    print("Query Response:")
    print(result)
