from dotenv import load_dotenv
import os
import argparse
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
)
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.astra_db import AstraDBVectorStore
from llama_index.llms.groq import Groq

os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"


def load_environment_variables():
    """Load and validate environment variables."""
    load_dotenv()

    required_vars = {
        "ASTRA_DB_ENDPOINT": os.getenv("ASTRA_DB_ENDPOINT"),
        "ASTRA_DB_TOKEN": os.getenv("ASTRA_DB_TOKEN"),
        "GROQ_API_TOKEN": os.getenv("GROQ_API_TOKEN"),
    }

    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    return required_vars


def create_vector_store(category, astra_token, astra_endpoint):
    """Create AstraDB vector store for the specified category."""
    return AstraDBVectorStore(
        token=astra_token,
        api_endpoint=astra_endpoint,
        collection_name=f"{category}_collections",
        embedding_dimension=768,
    )


def load_documents(category_path):
    """Load documents from the specified category directory."""
    documents = SimpleDirectoryReader(category_path).load_data(num_workers=10)
    print(f"Total documents loaded: {len(documents)}")
    if documents:
        print(f"First document ID: {documents[0].doc_id}")
        print(f"First document hash: {documents[0].hash}")
    return documents


def create_index(documents, vector_store):
    """Create vector store index with the specified documents."""
    embed_model = OllamaEmbedding(model_name="nomic-embed-text")
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, embed_model=embed_model
    )


def setup_query_engine(index, groq_token):
    """Set up the query engine with Groq LLM."""
    llm = Groq(model="deepseek-r1-distill-llama-70b", api_key=groq_token)
    return index.as_query_engine(llm=llm)


def main(category):
    """Main function to process documents for a specific category."""
    try:
        # Load environment variables
        env_vars = load_environment_variables()

        # Construct category path
        category_path = f"./data/{category}/"
        if not os.path.exists(category_path):
            raise ValueError(f"category directory not found: {category_path}")

        # Create vector store
        vector_store = create_vector_store(
            category, env_vars["ASTRA_DB_TOKEN"], env_vars["ASTRA_DB_ENDPOINT"]
        )

        # Load and process documents
        documents = load_documents(category_path)
        if not documents:
            raise ValueError(f"No documents found in {category_path}")

        # Create index
        index = create_index(documents, vector_store)
        print(f"Successfully created index for {category} category")

    except Exception as e:
        print(f"Error processing {category} category: {str(e)}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process documents for a specific category"
    )
    parser.add_argument(
        "category", help="category name (e.g., medical, tech, architectural)"
    )
    args = parser.parse_args()

    main(args.category)
