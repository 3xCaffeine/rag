#!/bin/sh

echo "Starting Ollama server..."
ollama serve &

OLLAMA_PID=$!

# Wait for Ollama server to be ready on port 11434 using /dev/tcp
echo "Waiting for Ollama server to become responsive..."
sleep 2

echo "Ollama server is up. Pulling the model..."
ollama pull nomic-embed-text

echo "Model pulled successfully. Continuing with Ollama server..."
wait "$OLLAMA_PID"
