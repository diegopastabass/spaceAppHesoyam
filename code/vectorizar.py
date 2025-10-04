import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# --------------------------------------------------------
# CONFIGURACIÓN DE RUTAS
# --------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "extracted_md")
OUTPUT_DIR = os.path.join(BASE_DIR, "vector_db")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --------------------------------------------------------
# CARGA DE DOCUMENTOS
# --------------------------------------------------------

documents = []
if not os.path.exists(DATA_DIR):
    raise FileNotFoundError(f"❌ No se encontró el directorio {DATA_DIR}")

for file in os.listdir(DATA_DIR):
    if file.endswith(".md"):
        path = os.path.join(DATA_DIR, file)
        with open(path, "r", encoding="utf-8") as f:
            documents.append({"filename": file, "content": f.read()})

print(f"📄 {len(documents)} documentos Markdown cargados desde {DATA_DIR}")

# --------------------------------------------------------
# CHUNKING (división del texto)
# --------------------------------------------------------

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
    length_function=len
)

chunks = []
for doc in documents:
    parts = splitter.split_text(doc["content"])
    for i, part in enumerate(parts):
        chunks.append({
            "filename": doc["filename"],
            "chunk_id": i,
            "content": part
        })

print(f"🧩 {len(chunks)} chunks generados en total")

# --------------------------------------------------------
# EMBEDDINGS (modelo Hugging Face)
# --------------------------------------------------------

# Modelo open-source optimizado para retrieval
model_name = "BAAI/bge-small-en-v1.5"

embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs={"device": "cpu"},  # usa 'cuda' si tienes GPU
    encode_kwargs={"normalize_embeddings": True}  # normaliza vectores (recomendado)
)

# --------------------------------------------------------
# VECTOR STORE (FAISS)
# --------------------------------------------------------

texts = [c["content"] for c in chunks]
metadatas = [{"source": c["filename"], "chunk_id": c["chunk_id"]} for c in chunks]

vectorstore = FAISS.from_texts(
    texts=texts,
    embedding=embeddings,
    metadatas=metadatas
)

vectorstore.save_local(OUTPUT_DIR)
print(f"✅ Base vectorial creada y guardada en {OUTPUT_DIR}")

# --------------------------------------------------------
# PRUEBA DE BÚSQUEDA
# --------------------------------------------------------

query = "How does microgravity affect plant development?"
results = vectorstore.similarity_search(query, k=3)

print("\n🔍 Resultados de búsqueda de prueba:")
for r in results:
    print(f"\n📘 Documento: {r.metadata['source']} (chunk {r.metadata['chunk_id']})")
    print(r.page_content[:300], "...")
