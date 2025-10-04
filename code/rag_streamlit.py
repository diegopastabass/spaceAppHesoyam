#!/usr/bin/env python3
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# =========================================================
# 1. Configuración inicial
# =========================================================
load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # evita deadlocks

st.set_page_config(page_title="RAG Chatbot", page_icon="🧬", layout="wide")
st.title("🧠 RAG Chatbot — BGE + Azure GPT-4o-mini")
st.caption("Asistente científico basado en recuperación de información con FAISS + Azure OpenAI")

# Inicializar modelos solo una vez
@st.cache_resource
def load_models():
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    db = FAISS.load_local("vector_db", embeddings, allow_dangerous_deserialization=True)

    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        temperature=0.2,
        max_retries=2,
        timeout=None,
    )
    return llm, db

llm, db = load_models()

# =========================================================
# 2. Inicializar sesión de chat
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================================================
# 3. Entrada del usuario
# =========================================================
if question := st.chat_input("Escribe tu pregunta aquí..."):
    # Mostrar pregunta del usuario
    st.chat_message("user").markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    # =========================================================
    # 4. Recuperar documentos relevantes
    # =========================================================
    with st.spinner("🔍 Buscando información relevante..."):
        docs_with_scores = db.similarity_search_with_score(question, k=5)

        # Filtrar por umbral de distancia (<= porque menor distancia = más similitud)
        THRESHOLD = 0.35
        relevant_docs = [(doc, score) for doc, score in docs_with_scores if score <= THRESHOLD]

    if not relevant_docs:
        response_text = "⚠️ No se encontraron documentos relevantes. La pregunta está fuera de dominio.\n\n**Respuesta:** I don't have enough information to answer."
        with st.chat_message("assistant"):
            st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})
    else:
        # Mostrar fuentes relevantes
        st.markdown("### 📚 Documentos más relevantes:")
        for i, (d, s) in enumerate(relevant_docs):
            fuente = d.metadata.get("source", "Desconocida")
            st.markdown(f"**[{i+1}]** `{fuente}` — distancia: `{s:.4f}`")

        # Crear contexto
        context = "\n\n".join(
            [f"Fuente: {d.metadata.get('source', 'Desconocida')}\n{d.page_content}" for d, _ in relevant_docs]
        )

        # =========================================================
        # 5. Generar respuesta con Azure GPT
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

        with st.spinner("🤖 Generando respuesta..."):
            result = llm.invoke(prompt)
            response_text = result.content

        with st.chat_message("assistant"):
            st.markdown(response_text)

        st.session_state.messages.append({"role": "assistant", "content": response_text})
