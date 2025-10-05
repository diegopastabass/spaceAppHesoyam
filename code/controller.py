# app.py
# -*- coding: utf-8 -*-
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from graph import build_agentic_graph

# Cargar variables de entorno
load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"

app = Flask(__name__)

# ===============================
# Carga del stack RAG
# ===============================
def load_stack():
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    db = FAISS.load_local("vector_db", embeddings, allow_dangerous_deserialization=True)
    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        temperature=0.2,
        max_retries=2,
    )
    graph = build_agentic_graph(llm, db)
    return graph

graph = load_stack()

# ===============================
# Endpoints
# ===============================

@app.route("/")
def index():
    return jsonify({
        "service": "Agentic RAG — NASA BioSciences",
        "status": "online",
        "description": "Chatbot que realiza clasificación de dominio, expansión de consultas y recuperación de contexto."
    })

@app.route("/ask", methods=["POST"])
def ask():
    """
    Espera un JSON:
    {
        "question": "¿Qué efecto tienen los vuelos espaciales prolongados en los músculos?"
    }
    """
    try:
        data = request.get_json()
        if not data or "question" not in data:
            return jsonify({"error": "Falta el campo 'question'."}), 400
        
        question = data["question"]
        state = {"question": question, "k_per_query": 3}
        out = graph.invoke(state)

        answer = out.get("answer_md", "No response.")
        related = out.get("related_with", [])

        return jsonify({
            "response": answer,
            "related_with": related
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Endpoint simple para ver si el servicio está operativo."""
    return jsonify({"status": "ok"})

# ===============================
# Lanzar servidor
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
