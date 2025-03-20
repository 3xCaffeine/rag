<h1>InfoRAG</h1>

---

InfoRAG is an AI-powered documentation assistant that leverages Retrieval-Augmented Generation (RAG) to provide accurate, context-aware responses to professional queries across various domains.

# Key Features:
- Knowledge-Based Ingestion Pipeline 
- Vector Embedding
- Multimodal Input Processing
- Chain-of-Thought Implementation to reduce <strong>hallucinations</strong>
# Overview:
![DiagramRAG](https://github.com/user-attachments/assets/a298c9a8-5687-4ed2-9d90-21020b1baffc)

# Tech Stack:
#### *Languages:*
- *Backend Framework:*  
  - *FastAPI* 
- *Frontend:*  
	- *NextJS*  
	- *TypeScript*  
#### *Models:*
- *Gemini*  
- *Deepseek R1 Distill Llama 70B* 
- *Nomic-Embed-Text*  
#### *Libraries:*
- *LlamaIndex:*  
- *Gemini Genai SDK:*  
- *Groq*  
- *AstraDB*  
#### *LlamaIndex Plugins:*
- *Tool Calling*  
- *Arxiv Plugin*  
- *PubMed Document API*   
#### *Toolchain:*
- *uv Package Manager* 
- *Docker* 
# Usage:
![image](https://github.com/user-attachments/assets/1c859ebf-e0eb-48d9-9cf9-efb268b7144c)

1. Choose Domain
2. Enter your Prompt
3. Enable Web Search(Stock Prices, Weather, API Requests, Current News)
4. Audio Input
5. Attach PDF/Image

```
docker run -d -p 8000:8000 -v $(pwd)/.env:/app/.env sasquatch06/rag-backend:latest
```
