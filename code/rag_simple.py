import os
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from tqdm import tqdm

# =========================================================
# 0. Configuración general
# =========================================================
# Evita warnings y bloqueos de Hugging Face Tokenizers
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Cargar variables de entorno
load_dotenv()

# =========================================================
# 1. Configurar modelo de lenguaje (Azure OpenAI)
# =========================================================
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

# =========================================================
# 2. Cargar modelo de embeddings Hugging Face
# =========================================================
print("🔹 Cargando modelo de embeddings: BAAI/bge-small-en-v1.5...")

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

# =========================================================
# 3. Cargar base vectorial FAISS
# =========================================================
print("📂 Cargando base vectorial desde 'vector_db'...")
vector_db_path = "vector_db"

if not os.path.exists(vector_db_path):
    raise FileNotFoundError("❌ No se encontró la base de datos vectorial en la carpeta 'vector_db'.")

db = FAISS.load_local(
    vector_db_path,
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 5})

# =========================================================
# 4. Interfaz interactiva en consola
# =========================================================
print("\n🚀 Sistema RAG (BGE + Azure GPT-4o-mini)")
print("💬 Escribe tu pregunta o 'salir' para terminar.\n")

while True:
    try:
        question = input("❓ Pregunta: ").strip()
        if question.lower() in ["salir", "exit", "quit"]:
            print("👋 Saliendo del sistema RAG. ¡Hasta luego!")
            break

        if not question:
            continue

        # =========================================================
        # 5. Recuperar documentos relevantes
        # =========================================================
        print("\n⏳ Buscando información relevante...\n")
        docs = retriever.get_relevant_documents(question)

        if not docs:
            print("⚠️ No se encontraron documentos relevantes.")
            continue

        print("📚 Documentos más relevantes:")
        for i, d in enumerate(docs[:5]):
            fuente = d.metadata.get("source", "Desconocida")
            print(f"   [{i+1}] Fuente: {fuente}")

        # Crear contexto con texto + fuente
        context = "\n\n".join(
            [f"Fuente: {d.metadata.get('source', 'Desconocida')}\n{d.page_content}" for d in docs[:5]]
        )

        # =========================================================
        # 6. Generar respuesta con el LLM (prompt contextual)
        # =========================================================
        prompt = f"""
You are a biomedical research assistant.
Answer the user's question **only** using the information in the provided sources.
If the answer cannot be found, say: "I don't have enough information to answer."

### Sources:
{context}

### Question:
{question}

Your answer should include clear reasoning and cite the most relevant source(s).
        """

        response = llm.invoke(prompt)
        print("\n🧠 Respuesta:")
        print(response.content)
        print("\n------------------------------------------------------------\n")

    except KeyboardInterrupt:
        print("\n👋 Interrupción detectada. Cerrando el sistema.")
        break
    except Exception as e:
        print(f"❌ Error: {e}")
        continue
