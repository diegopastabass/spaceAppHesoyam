#!/usr/bin/env python3
import os
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tqdm import tqdm

# =========================================================
# 1. Configuración inicial
# =========================================================
load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Evita deadlocks de tokenizers

# Modelo de lenguaje
print("🤖 Inicializando modelo Azure OpenAI (gpt-4o-mini)...")
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    temperature=0.2,
    max_retries=2,
    timeout=None,
)
parser = StrOutputParser()

# Embeddings
print("🔹 Cargando modelo de embeddings: BAAI/bge-small-en-v1.5...")
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

# Cargar base vectorial
print("📂 Cargando base vectorial desde vector_db...")
db = FAISS.load_local("vector_db", embeddings, allow_dangerous_deserialization=True)

# =========================================================
# 2. Loop de preguntas del usuario
# =========================================================
print("\n🚀 Sistema RAG (BGE + Azure GPT-4o-mini)")
print("💬 Escribe tu pregunta o 'salir' para terminar.\n")

while True:
    try:
        question = input("❓ Pregunta: ").strip()
        if question.lower() in ["salir", "exit", "quit"]:
            print("\n👋 Saliendo del sistema RAG.")
            break

        # =========================================================
        # 3. Recuperar documentos relevantes con límite de distancia
        # =========================================================
        print("\n⏳ Buscando información relevante...\n")

        # Recupera documentos con sus scores de similitud
        docs_with_scores = db.similarity_search_with_score(question, k=5)

        # Definir el umbral de similitud (ajustable)
        THRESHOLD = 0.35  # <= 0.35 para BAAI/bge-small-en-v1.5
        relevant_docs = [(doc, score) for doc, score in docs_with_scores if score <= THRESHOLD]

        if not relevant_docs:
            print("⚠️ No se encontraron documentos relevantes (la pregunta está fuera de dominio).")
            print("\n🧠 Respuesta:")
            print("I don't have enough information to answer.")
            print("\n------------------------------------------------------------\n")
            continue

        # Mostrar documentos relevantes
        print("📚 Documentos más relevantes:")
        for i, (d, s) in enumerate(relevant_docs):
            fuente = d.metadata.get("source", "Desconocida")
            print(f"   [{i+1}] Fuente: {fuente} — Distancia: {s:.4f}")

        # Crear contexto con texto + fuente
        context = "\n\n".join(
            [f"Fuente: {d.metadata.get('source', 'Desconocida')}\n{d.page_content}" for d, _ in relevant_docs]
        )

        # =========================================================
        # 4. Generar respuesta con el modelo Azure GPT
        # =========================================================
        prompt = f"""
Eres un asistente científico. Responde a la pregunta del usuario **basándote únicamente** en el siguiente contexto.
Si la información no es suficiente o no es relevante, responde: "No tengo suficiente información para responder."

Por favor, entrega la respuesta en **formato Markdown**, incluyendo:
- Una explicación estructurada y clara.
- Uso de subtítulos o viñetas si corresponde.
- Destaca nombres de proteínas, genes o vías de señalización en *itálicas* o **negritas**.
- Añade un breve resumen al final bajo el título **Resumen**.

---
### 🧩 Contexto:
{context}

### ❓ Pregunta:
{question}

---
### 🧠 Respuesta en formato Markdown:
"""

        response = llm.invoke(prompt)
        print("\n🧠 Respuesta:")
        print(response.content)
        print("\n------------------------------------------------------------\n")

    except KeyboardInterrupt:
        print("\n👋 Interrupción detectada. Saliendo...")
        break
    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")
        continue
