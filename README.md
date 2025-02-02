<h1><center> RAG-narok</center></h1>

---

<center> RAG-narok is an AI-powered documentation assistant that leverages Retrieval-Augmented Generation (RAG) to provide accurate, context-aware responses to professional queries across various domains..</center> 

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

```
docker run -d -p 8000:8000 -v $(pwd)/.env:/app/.env sasquatch06/rag-backend:latest
```
