from dotenv import load_dotenv
import os

os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

from llama_index.vector_stores.astra_db import AstraDBVectorStore

load_dotenv()

astra_api_endpoint = os.getenv("ASTRA_DB_ENDPOINT")
astra_db_token = os.getenv("ASTRA_DB_TOKEN")
astra_db_store = AstraDBVectorStore(
    token=astra_db_token,
    api_endpoint=astra_api_endpoint,
    collection_name="pdf_collections",
    embedding_dimension=768,
)

if __name__ == "__main__":
    try:
        # Test connection by getting collection info
        collection_info = astra_db_store._collection.find_one()
        print("Successfully connected to Astra DB")
        print(f"Collection info: {collection_info}")
        print(f"{astra_db_store._collection.name} has been created")
    except Exception as e:
        print(f"Error connecting to Astra DB: {e}")
