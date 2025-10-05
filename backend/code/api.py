# -*- coding: utf-8 -*-
import os
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from code.graph import build_agentic_graph


load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"

app = FastAPI(title="Agentic RAG — NASA Bio API", version="1.0.0")

# CORS: permitir frontends locales (Vite: 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Hackathon: abrir a todos para evitar bloqueos durante desarrollo
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str = Field(..., description="Pregunta del usuario en español sobre biología/vida en el espacio")
    k_per_query: Optional[int] = Field(6, description="Número de documentos por consulta expandida")


class ChatResponse(BaseModel):
    answer_md: str


graph = None
last_startup_error: Optional[str] = None


def _load_stack():
    print("[startup] Cargando embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    print("[startup] Cargando FAISS desde 'vector_db'...")
    db = FAISS.load_local("vector_db", embeddings, allow_dangerous_deserialization=True)
    print("[startup] Inicializando AzureChatOpenAI...")
    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        temperature=0.1,
        max_retries=2,
    )
    print("[startup] Construyendo grafo agentico...")
    g = build_agentic_graph(llm, db)
    print("[startup] Grafo cargado OK")
    return g


@app.on_event("startup")
def startup_event():
    global graph, last_startup_error
    try:
        graph = _load_stack()
        last_startup_error = None
    except Exception as e:
        # Permitimos arrancar para devolver 503 luego, pero registramos el error
        graph = None
        last_startup_error = str(e)
        print(f"[startup] Error cargando stack RAG: {e}")


@app.get("/")
def healthcheck() -> Dict[str, Any]:
    status = "ok" if graph is not None else "error"
    body: Dict[str, Any] = {
        "service": "SpaceApp Hesoyam - Agentic RAG",
        "description": "Sistema RAG para análisis de documentos científicos de NASA BioSciences",
        "version": "1.0.0",
        "status": status,
        "graph_loaded": graph is not None,
        "capabilities": [
            "Clasificación de dominio",
            "Expansión de consultas",
            "Recuperación de contexto",
            "Generación de respuestas con citas",
            "Evaluación de distancias de documentos",
        ],
    }
    if last_startup_error:
        body["error"] = last_startup_error
    # Variables críticas para diagnósticos
    body["env"] = {
        "AZURE_OPENAI_ENDPOINT_set": bool(os.getenv("AZURE_OPENAI_ENDPOINT")),
        "AZURE_OPENAI_API_KEY_set": bool(os.getenv("AZURE_OPENAI_API_KEY")),
        "AZURE_OPENAI_DEPLOYMENT": os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION"),
    }
    return body


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if graph is None:
        raise HTTPException(status_code=503, detail="RAG no disponible (stack no cargado)")

    try:
        state = {"question": req.question, "k_per_query": req.k_per_query or 6}
        print(f"[/chat] Pregunta: {req.question}")
        print(f"[/chat] k_per_query: {state['k_per_query']}")
        out = graph.invoke(state)
        # Trazas de salida relevantes
        if isinstance(out, dict):
            ctx_len = len(out.get("context_text", "")) if out.get("context_text") else 0
            filt = out.get("filtered") or []
            print(f"[/chat] context_text_len={ctx_len} filtered_docs={len(filt)}")
        answer = out.get("answer_md", "No response.")
        return ChatResponse(answer_md=answer)
    except HTTPException:
        raise
    except Exception as e:
        print(f"[/chat] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error al generar respuesta: {e}")


