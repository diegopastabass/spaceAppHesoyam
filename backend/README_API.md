### Agentic RAG — NASA Bio API

Expone el mismo flujo que `code/rag_agentico.py` (input `question` → output `answer_md`). Reutiliza `vector_db/` (FAISS) y `code/graph.py`.

### Endpoints
- GET `/`: healthcheck `{ status, graph_loaded }`
- POST `/chat`: ejecuta el grafo RAG

### Entrada (POST /chat)
```json
{
  "question": "...",
  "k_per_query": 6
}
```
- `question`: obligatorio (español)
- `k_per_query`: opcional, por defecto 6

### Salida
```json
{
  "answer_md": "respuesta en Markdown"
}
```

### Ejemplos cURL
En dominio:
```bash
curl -s -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"question":"¿Cómo afectó la microgravedad a la expresión génica en el sistema nervioso central de los caracoles Helix aspersa durante las misiones Foton M-2 y M-3?", "k_per_query":6}' | jq
```
Fuera de dominio:
```bash
curl -s -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"question":"¿Cómo comprar un iPhone?"}' | jq
```

### Ejecutar
1) Variables de entorno (Azure OpenAI):
```bash
export AZURE_OPENAI_ENDPOINT="https://<endpoint>.openai.azure.com"
export AZURE_OPENAI_API_KEY="<api-key>"
export AZURE_OPENAI_DEPLOYMENT="gpt-4o-mini"
export AZURE_OPENAI_API_VERSION="2024-12-01-preview"
```
2) Instalar deps:
```bash
pip install fastapi uvicorn python-dotenv langchain-openai langchain-community langgraph faiss-cpu sentence-transformers
```
3) Levantar API:
```bash
uvicorn code.api:app --host 0.0.0.0 --port 8000
```
