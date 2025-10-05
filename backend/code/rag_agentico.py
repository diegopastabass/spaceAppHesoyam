# main.py
# -*- coding: utf-8 -*-
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from graph import build_agentic_graph

load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"

st.set_page_config(page_title="Agentic RAG — NASA Bio", page_icon="🧬", layout="wide")
st.title("🧠 Agentic RAG — NASA BioSciences")
st.caption("Chatbot: clasificación de dominio → expansión de consultas → recuperación → GraphRAG ligero → respuesta con citas")

@st.cache_resource
def load_stack():
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    db = FAISS.load_local("vector_db", embeddings, allow_dangerous_deserialization=True)
    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        temperature=0.1,
        max_retries=2,
    )
    graph = build_agentic_graph(llm, db)
    return graph

graph = load_stack()

if "messages" not in st.session_state:
    st.session_state.messages = []

# muestra historial
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# input del chat
question = st.chat_input("Escribe tu pregunta contexto NASA Biosciences / Space Life Sciences")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.spinner("Pensando..."):
        # defaults internos: k=3, umbral auto (0.70 si similitud, 0.35 si distancia)
        state = {"question": question, "k_per_query": 6}
        out = graph.invoke(state)

    answer = out.get("answer_md", "No response.")
    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})