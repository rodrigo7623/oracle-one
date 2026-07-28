"""Indexa el PDF fuente en un vectorstore FAISS.

Uso: python -m app.ingest
Debe ejecutarse una vez (o cada vez que cambie el documento fuente) antes
de levantar la API. El índice generado se persiste en storage/faiss_index
y luego se carga en memoria en cada arranque de app/agent.py.
"""
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import CHUNK_OVERLAP, CHUNK_SIZE, EMBEDDING_MODEL_NAME, INDEX_DIR, PDF_PATH


def build_vectorstore() -> FAISS:
    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el documento fuente en {PDF_PATH}. "
            "Ejecutá primero: python scripts/generar_pdf.py"
        )

    pages = PyPDFLoader(str(PDF_PATH)).load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n\n", "\n", ". ", " "],
    )
    chunks = splitter.split_documents(pages)

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectorstore = FAISS.from_documents(chunks, embeddings)

    INDEX_DIR.parent.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(INDEX_DIR))
    print(f"Índice FAISS creado con {len(chunks)} fragmentos en {INDEX_DIR}")
    return vectorstore


if __name__ == "__main__":
    build_vectorstore()
